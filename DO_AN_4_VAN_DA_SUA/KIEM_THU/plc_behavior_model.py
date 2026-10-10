"""Independent scan model for reviewing the fountain requirements.

Not a Siemens runtime, SCL interpreter, TIA compiler, or hardware simulation.
Time is an integer monotonic millisecond counter; wall time is a separate input.
Output bits 0..3 correspond to valves YV1..YV4.
"""
from dataclasses import dataclass, field


def rtc_success(return_code: int, hour: int, minute: int, second: int = 0) -> bool:
    return return_code in (0, 1) and 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60


def schedule(hour: int, minute: int, valid: bool = True) -> bool:
    if not valid or not (0 <= hour <= 23 and 0 <= minute <= 59):
        return False
    t = 60 * hour + minute
    return 360 <= t < 480 or 1020 <= t < 1230


@dataclass
class Inputs:
    auto: bool = False
    reset: bool = False
    stop_ok: bool = True
    estop_ok: bool = True
    water_ok: bool = True
    overload_ok: bool = True
    rtc_valid: bool = True
    hour: int = 6
    minute: int = 0
    first_scan: bool = False


@dataclass(frozen=True)
class Output:
    pump: bool
    mask: int
    step: int
    elapsed_ms: int
    armed: bool
    in_schedule: bool
    fault_bits: int
    stop_latched: bool
    fault_code: int
    alarm_bits: int
    reset_allowed: bool


@dataclass
class ScanModel:
    state: int = 0
    armed: bool = False
    saw_off: bool = False
    stop_memory: bool = False
    fault_memory: int = 0
    prev_auto: bool = False
    prev_reset: bool = False
    timer_start: list = field(default_factory=lambda: [None] * 5)
    last_scan: int = -1

    def scan(self, ms: int, i: Inputs) -> Output:
        if ms <= self.last_scan:
            raise ValueError("Scan timestamps must increase monotonically")
        self.last_scan = ms
        if i.first_scan:
            self.state = 0
            self.armed = False
            self.saw_off = not i.auto
            self.stop_memory = False
            self.fault_memory = 0
            self.prev_auto = i.auto
            self.prev_reset = i.reset
        auto_edge = i.auto and not self.prev_auto and not i.first_scan
        reset_edge = i.reset and not self.prev_reset and not i.first_scan
        self.prev_auto, self.prev_reset = i.auto, i.reset
        safe = i.stop_ok and i.estop_ok and i.water_ok and i.overload_ok
        clock_ok = i.rtc_valid and 0 <= i.hour < 24 and 0 <= i.minute < 60
        sched = schedule(i.hour, i.minute, clock_ok)
        for bit, condition in enumerate((not i.estop_ok, not i.water_ok,
                                         not i.overload_ok, i.auto and not clock_ok)):
            if condition:
                self.fault_memory |= 1 << bit
        if not i.stop_ok:
            self.stop_memory = True
        if not i.auto:
            self.armed = False
            self.saw_off = True
        if self.fault_memory or self.stop_memory:
            self.armed = False
        reset_allowed = not i.auto and safe and clock_ok and not i.first_scan
        if reset_edge and reset_allowed:
            self.fault_memory = 0
            self.stop_memory = False
        if auto_edge and self.saw_off and safe and clock_ok and not self.fault_memory and not self.stop_memory:
            self.armed = True
        running = (not i.first_scan and i.auto and self.armed and sched and safe
                   and not self.fault_memory and not self.stop_memory)
        if not running:
            self.state = 0
        elif self.state not in range(1, 6):
            self.state = 1

        elapsed = 0
        expired = False
        for idx in range(5):
            active = running and self.state == idx + 1
            if not active:
                self.timer_start[idx] = None
            else:
                if self.timer_start[idx] is None:
                    self.timer_start[idx] = ms
                elapsed = min(ms - self.timer_start[idx], 10000)
                expired = elapsed == 10000
        if running and expired:
            self.state = self.state % 5 + 1
            elapsed = 0
        # Output decoder written as predicates rather than expected mask table.
        valve_bits = (running and 1 <= self.state <= 4,
                      running and 2 <= self.state <= 5,
                      running and self.state in (3, 4),
                      running and self.state in (4, 5))
        mask = sum(int(v) << bit for bit, v in enumerate(valve_bits))
        fault_code = next((bit + 1 for bit in range(4)
                           if self.fault_memory & (1 << bit)), 0)
        alarm_bits = self.fault_memory | (16 if self.stop_memory else 0)
        return Output(bool(running), mask, self.state, elapsed, self.armed,
                      sched, self.fault_memory, self.stop_memory, fault_code,
                      alarm_bits, reset_allowed)
