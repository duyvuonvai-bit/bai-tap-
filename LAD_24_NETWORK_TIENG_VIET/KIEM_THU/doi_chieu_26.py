"""Independent scan model of supplied LAD images and the 26-network revision.

This is Python, not a Siemens runtime/compiler. TON uses monotonic timestamps,
all five timers are called each scan, and process-image I/O is sampled once per
scan. Hardware delays, contact bounce, CPU firmware, TIA type-checking and actual
safety circuitry are outside this model. No third-party packages are required.
"""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Inputs:
    auto: bool = False
    water: bool = True
    reset: bool = False
    estop_ok: bool = True
    overload_ok: bool = True
    stop_ok: bool = True
    rtc_status: int = 0
    hour: int = 7
    minute: int = 0
    second: int = 0

@dataclass
class TON:
    start_ms: int | None = None
    q: bool = False
    et_ms: int = 0

    def call(self, enabled: bool, now_ms: int, pt_ms: int = 10_000) -> bool:
        if not enabled:
            self.start_ms = None
            self.q = False
            self.et_ms = 0
        else:
            if self.start_ms is None:
                self.start_ms = now_ms
            self.et_ms = min(now_ms - self.start_ms, pt_ms)
            self.q = now_ms - self.start_ms >= pt_ms
        return self.q

class LADModel:
    """revision='original36' reproduces image logic; 'revised26' applies spec."""
    def __init__(self, revision='original36'):
        if revision not in ('original36', 'revised26'):
            raise ValueError(revision)
        self.revision = revision
        self.init_pending = revision == 'revised26'
        self.fault = self.stop_latched = self.off_seen = self.armed = False
        self.old_reset = self.old_auto = False
        self.step = self.next_step = 0
        self.timers = [TON() for _ in range(5)]
        self.last_ms = None

    def scan(self, inp: Inputs, now_ms: int) -> dict:
        if self.last_ms is not None and now_ms <= self.last_ms:
            raise ValueError('Model scans need strictly increasing monotonic time')
        self.last_ms = now_ms
        improved = self.revision == 'revised26'
        first_scan = improved and self.init_pending
        if first_scan:
            self.fault = self.stop_latched = self.off_seen = self.armed = False
            self.step = self.next_step = 0
        rtc_ok = inp.rtc_status == 0
        if improved:
            rtc_ok = (inp.rtc_status in (0, 1) and 0 <= inp.hour <= 23
                      and 0 <= inp.minute <= 59 and 0 <= inp.second <= 59)
        morning = rtc_ok and 6 <= inp.hour < 8
        evening = rtc_ok and (17 <= inp.hour < 20 or
                             inp.hour == 20 and inp.minute < 30)
        in_schedule = morning or evening
        safe = inp.water and inp.estop_ok and inp.overload_ok and inp.stop_ok
        bad_step = not 0 <= self.step <= 5
        fault_now = not inp.water or not inp.estop_ok or not inp.overload_ok
        if improved:
            fault_now = fault_now or (inp.auto and not rtc_ok) or bad_step
        reset_edge = inp.reset and not self.old_reset and not first_scan
        auto_edge = inp.auto and not self.old_auto and not first_scan
        self.old_reset, self.old_auto = inp.reset, inp.auto
        ack = reset_edge and not inp.auto and safe
        if improved:
            ack = ack and rtc_ok and not bad_step and not first_scan
        # Siemens SR with R1 is reset dominant.
        self.fault = (self.fault or fault_now) and not ack
        self.stop_latched = (self.stop_latched or not inp.stop_ok) and not ack
        if not inp.auto:
            self.off_seen = True
        cancel = (not inp.auto or not safe or self.fault or
                  self.stop_latched or not rtc_ok or first_scan)
        arm_request = (auto_edge and self.off_seen and safe and rtc_ok and
                       not self.fault and not self.stop_latched and not first_scan)
        self.armed = (self.armed or arm_request) and not cancel
        run = (self.armed and inp.auto and in_schedule and safe and
               not self.fault and not self.stop_latched and not first_scan)
        self.next_step = self.step
        if not run:
            self.next_step = 0
        if run and self.step == 0:
            self.next_step = 1
        # All calls see the SAME CurrentStep; only NextStep can change here.
        done = [timer.call(run and self.step == n, now_ms)
                for n, timer in enumerate(self.timers, 1)]
        for n, q in enumerate(done, 1):
            if self.step == n and q and (run or not improved):
                self.next_step = n + 1 if n < 5 else 1
        self.step = self.next_step
        if improved:
            output_enable = run and 1 <= self.step <= 5
            valves = (output_enable and self.step <= 4,
                      output_enable and self.step >= 2,
                      output_enable and 3 <= self.step <= 4,
                      output_enable and self.step >= 4)
            pump = output_enable
            alarm = self.fault
        else:
            valves = (run and 1 <= self.step <= 4,
                      run and 2 <= self.step <= 5,
                      run and 3 <= self.step <= 4,
                      run and 4 <= self.step <= 5)
            pump = run and safe and any(valves)
            alarm = self.fault or (inp.auto and not rtc_ok)
        self.init_pending = False
        return {'revision': self.revision, 'time_ms': now_ms,
                'first_scan': first_scan, 'rtc_ok': rtc_ok,
                'in_schedule': in_schedule, 'safe': safe,
                'fault_now': fault_now, 'bad_step_detected': bad_step,
                'fault_latched': self.fault, 'stop_latched': self.stop_latched,
                'off_seen': self.off_seen, 'reset_edge': reset_edge,
                'auto_edge': auto_edge, 'ack': ack, 'armed': self.armed,
                'run': run, 'step': self.step, 'pump': pump,
                'valves': list(valves),
                'mask': sum((1 << i) for i, on in enumerate(valves) if on),
                'alarm': alarm, 'timer_done': done,
                'timer_et_ms': [t.et_ms for t in self.timers]}

if __name__ == '__main__':
    import json
    model = LADModel('revised26')
    print(json.dumps(model.scan(Inputs(), 0), indent=2))
    print(json.dumps(model.scan(Inputs(auto=True), 10), indent=2))
