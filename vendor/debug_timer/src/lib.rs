//! Vendored copy of Blitz's `debug_timer` that prints exact nanosecond phase
//! durations on one machine-readable line (`PHASES <message>| total=ns name=ns ...`).
#[cfg(feature = "enable")]
mod real_debug_timer {
    use std::io::{stdout, Write};
    use std::time::Instant;

    pub struct DebugTimer {
        recorded_times: Vec<(&'static str, Instant)>,
    }

    impl DebugTimer {
        pub fn init() -> Self {
            Self { recorded_times: vec![("start", Instant::now())] }
        }
        pub fn record_time(&mut self, message: &'static str) {
            self.recorded_times.push((message, Instant::now()));
        }
        pub fn print_times(&self, message: &str) {
            let now = Instant::now();
            let total = (now - self.recorded_times[0].1).as_nanos();
            let mut out = stdout().lock();
            write!(out, "PHASES {message}| total={total}").unwrap();
            for pair in self.recorded_times.windows(2) {
                let d = pair[1].1.duration_since(pair[0].1).as_nanos();
                write!(out, " {}={d}", pair[1].0).unwrap();
            }
            writeln!(out).unwrap();
        }
    }
}

mod dummy_debug_timer {
    pub struct DebugTimer;
    impl DebugTimer {
        pub fn init() -> Self { Self }
        pub fn record_time(&mut self, _message: &'static str) {}
        pub fn print_times(&self, _message: &str) {}
    }
}

#[cfg(feature = "enable")]
#[macro_export]
macro_rules! debug_timer {
    ($id:ident, $($cond:tt)*) => {
        let mut $id = {
            #[cfg($($cond)*)]
            let timer = $crate::RealDebugTimer::init();
            #[cfg(not($($cond)*))]
            let timer = $crate::DummyDebugTimer::init();
            timer
        };
    };
}

#[cfg(feature = "enable")]
#[macro_export]
macro_rules! debug_timer_type {
    ($id:ident, $($cond:tt)*) => {
        #[cfg($($cond)*)]
        pub type $id = $crate::RealDebugTimer;
        #[cfg(not($($cond)*))]
        pub type $id = $crate::DummyDebugTimer;
    };
}

#[cfg(not(feature = "enable"))]
#[macro_export]
macro_rules! debug_timer {
    ($id:ident, $($cond:tt)*) => {
        let mut $id = $crate::DummyDebugTimer::init();
    };
}

#[cfg(not(feature = "enable"))]
#[macro_export]
macro_rules! debug_timer_type {
    ($id:ident, $($cond:tt)*) => {
        pub type $id = $crate::DummyDebugTimer;
    };
}

pub use dummy_debug_timer::DebugTimer as DummyDebugTimer;
#[cfg(feature = "enable")]
pub use real_debug_timer::DebugTimer as RealDebugTimer;
