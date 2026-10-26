//! Reads servoshell's perfetto trace (`--features tracing-perfetto`) and prints the spans run.py samples,
//! one JSON object per line: `{"name", "ts", "dur", "track", "thread", "webview"}`. A round's trace runs to
//! GBs (every layout query a page script makes is a `handle_reflow` span), so it is streamed packet by
//! packet and decoded with just the fields below; protobuf skips the rest.

use prost::Message;
use std::collections::HashMap;
use std::io::{BufWriter, Read, Write};

#[derive(Clone, PartialEq, Message)]
struct TracePacket {
    #[prost(uint64, optional, tag = "8")]
    timestamp: Option<u64>,
    #[prost(message, optional, tag = "11")]
    track_event: Option<TrackEvent>,
    #[prost(message, optional, tag = "60")]
    track_descriptor: Option<TrackDescriptor>,
}

#[derive(Clone, PartialEq, Message)]
struct TrackEvent {
    #[prost(int32, optional, tag = "9")]
    r#type: Option<i32>,
    #[prost(string, optional, tag = "23")]
    name: Option<String>,
    #[prost(uint64, optional, tag = "11")]
    track_uuid: Option<u64>,
    #[prost(message, repeated, tag = "4")]
    debug_annotations: Vec<DebugAnnotation>,
}

#[derive(Clone, PartialEq, Message)]
struct TrackDescriptor {
    #[prost(uint64, optional, tag = "1")]
    uuid: Option<u64>,
    #[prost(message, optional, tag = "4")]
    thread: Option<ThreadDescriptor>,
}

#[derive(Clone, PartialEq, Message)]
struct ThreadDescriptor {
    #[prost(string, optional, tag = "5")]
    thread_name: Option<String>,
}

#[derive(Clone, PartialEq, Message)]
struct DebugAnnotation {
    #[prost(string, optional, tag = "10")]
    name: Option<String>,
    #[prost(bool, optional, tag = "2")]
    bool_value: Option<bool>,
    #[prost(uint64, optional, tag = "3")]
    uint_value: Option<u64>,
    #[prost(int64, optional, tag = "4")]
    int_value: Option<i64>,
    #[prost(double, optional, tag = "5")]
    double_value: Option<f64>,
    #[prost(string, optional, tag = "6")]
    string_value: Option<String>,
}

impl DebugAnnotation {
    fn value(&self) -> Option<String> {
        self.string_value
            .clone()
            .or_else(|| self.int_value.map(|v| v.to_string()))
            .or_else(|| self.uint_value.map(|v| v.to_string()))
            .or_else(|| self.bool_value.map(|v| if v { "True".into() } else { "False".into() }))
            .or_else(|| self.double_value.map(|v| v.to_string()))
    }
}

const TYPE_SLICE_BEGIN: i32 = 1;
const TYPE_SLICE_END: i32 = 2;

/// The spans the samples use; a `handle_reflow` is kept only if it encloses one of the others.
const SPANS: [&str; 8] = [
    "handle_reflow",
    "prepare_stylist_for_reflow",
    "restyle_and_build_trees",
    "Styling",
    "Box Tree Construction",
    "Fragment Tree Construction",
    "Stacking Context Tree Construction",
    "Display List Construction",
];

fn json_string(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

/// Calls `f` with every length-delimited `packet` (field 1) of the trace, in order.
fn for_each_packet(mut input: impl Read, mut f: impl FnMut(&[u8])) -> std::io::Result<()> {
    let mut buf = Vec::with_capacity(64 << 20);
    let mut chunk = vec![0u8; 16 << 20];
    loop {
        let n = input.read(&mut chunk)?;
        if n == 0 {
            break;
        }
        buf.extend_from_slice(&chunk[..n]);
        let mut i = 0;
        loop {
            // tag varint, then length varint, then the packet; stop at a partial record
            let mut j = i;
            while j < buf.len() && buf[j] & 0x80 != 0 {
                j += 1;
            }
            if j + 1 >= buf.len() {
                break;
            }
            j += 1;
            let (mut len, mut shift) = (0usize, 0);
            let mut complete = false;
            while j < buf.len() {
                let b = buf[j];
                j += 1;
                len |= ((b & 0x7f) as usize) << shift;
                shift += 7;
                if b & 0x80 == 0 {
                    complete = true;
                    break;
                }
            }
            if !complete || j + len > buf.len() {
                break;
            }
            f(&buf[j..j + len]);
            i = j + len;
        }
        buf.drain(..i);
    }
    Ok(())
}

fn main() -> std::io::Result<()> {
    let path = std::env::args().nth(1).expect("usage: servo-trace <servo.pftrace>");
    let file = std::fs::File::open(&path)?;
    let mut out = BufWriter::new(std::io::stdout().lock());
    let mut threads: HashMap<u64, String> = HashMap::new();
    let mut open: HashMap<u64, Vec<(String, u64, Option<String>)>> = HashMap::new();
    let mut last_kept: HashMap<u64, u64> = HashMap::new();
    for_each_packet(file, |bytes| {
        let Ok(packet) = TracePacket::decode(bytes) else { return };
        if let Some(d) = packet.track_descriptor {
            if let (Some(uuid), Some(name)) = (d.uuid, d.thread.and_then(|t| t.thread_name)) {
                threads.insert(uuid, name);
            }
            return;
        }
        let Some(event) = packet.track_event else { return };
        let (track, ts) = (event.track_uuid.unwrap_or(0), packet.timestamp.unwrap_or(0));
        let stack = open.entry(track).or_default();
        match event.r#type {
            Some(TYPE_SLICE_BEGIN) => {
                let webview = event
                    .debug_annotations
                    .iter()
                    .find(|a| a.name.as_deref() == Some("webview_id"))
                    .and_then(DebugAnnotation::value);
                stack.push((event.name.unwrap_or_default(), ts, webview));
            }
            Some(TYPE_SLICE_END) => {
                let Some((name, begin, webview)) = stack.pop() else { return };
                if !SPANS.contains(&name.as_str()) {
                    return;
                }
                if name == "handle_reflow" && last_kept.get(&track).map_or(true, |&kept| kept < begin) {
                    return;
                }
                last_kept.insert(track, begin);
                let webview = webview.map_or_else(|| "null".to_string(), |w| json_string(&w));
                writeln!(
                    out,
                    "{{\"name\":{},\"ts\":{},\"dur\":{},\"track\":{},\"thread\":{},\"webview\":{}}}",
                    json_string(&name),
                    begin,
                    ts - begin,
                    track,
                    json_string(threads.get(&track).map_or("", String::as_str)),
                    webview
                )
                .unwrap();
            }
            _ => {}
        }
    })?;
    out.flush()
}
