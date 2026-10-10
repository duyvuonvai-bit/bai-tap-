"""Run: python -m unittest -v test_plc_behavior.py (in this directory).

Tests the Python requirements/scan model. Does NOT compile or execute SCL.
"""
import random
import unittest
from dataclasses import replace
from plc_behavior_model import Inputs, ScanModel, rtc_success, schedule


class FountainRequirementTests(unittest.TestCase):
    def setUp(self):
        self.plc = ScanModel()
        self.i = Inputs()
        self.ms = 0
        self.plc.scan(0, replace(self.i, first_scan=True))

    def scan(self, **changes):
        self.i = replace(self.i, **changes)
        self.ms += 10
        return self.plc.scan(self.ms, self.i)

    def start(self):
        out = self.scan(auto=True)
        self.assertTrue(out.pump)
        self.assertEqual((out.step, out.mask), (1, 1))
        return out

    def test_01_all_daily_minutes_match_assigned_windows(self):
        # Independent oracle: ranges explicitly enumerate the assigned minutes.
        expected = set(range(6 * 60, 8 * 60)) | set(range(17 * 60, 20 * 60 + 30))
        actual = {m for m in range(1440) if schedule(*divmod(m, 60))}
        self.assertEqual(actual, expected)

    def test_02_boundaries_with_seconds(self):
        for h, m, s, result in ((5, 59, 59, False), (6, 0, 0, True),
                               (7, 59, 59, True), (8, 0, 0, False),
                               (16, 59, 59, False), (17, 0, 0, True),
                               (20, 29, 59, True), (20, 30, 0, False)):
            with self.subTest(h=h, m=m, s=s):
                self.assertEqual(schedule(h, m), result)

    def test_03_bad_clock_values_rejected(self):
        for h, m in ((-1, 0), (24, 0), (6, -1), (6, 60), (32767, 32767)):
            with self.subTest(h=h, m=m):
                self.assertFalse(schedule(h, m))
        self.assertFalse(schedule(6, 0, valid=False))

    def test_04_rtc_standard_and_daylight_success_codes(self):
        self.assertTrue(rtc_success(0, 6, 0))
        self.assertTrue(rtc_success(1, 6, 0))
        for rc in (2, -32640, 0x8080, 0x8081):
            self.assertFalse(rtc_success(rc, 6, 0))
        self.assertFalse(rtc_success(0, 6, 0, 60))

    def test_05_powerup_auto_held_stays_off_until_off_seen(self):
        plc = ScanModel()
        i = Inputs(auto=True, first_scan=True)
        self.assertFalse(plc.scan(0, i).pump)
        self.assertFalse(plc.scan(10, replace(i, first_scan=False)).pump)
        self.assertFalse(plc.scan(20, replace(i, auto=False, first_scan=False)).pump)
        self.assertTrue(plc.scan(30, replace(i, first_scan=False)).pump)

    def test_06_off_always_disables_all_outputs(self):
        self.start()
        out = self.scan(auto=False)
        self.assertEqual((out.pump, out.mask, out.step), (False, 0, 0))

    def test_07_two_cycles_correct_masks_and_nominal_duration(self):
        out = self.start()
        changes = [(self.ms, out.step, out.mask)]
        for _ in range(10100):
            out = self.scan()
            self.assertTrue(out.pump, "Pump must stay on across all step transitions")
            if out.step != changes[-1][1]:
                changes.append((self.ms, out.step, out.mask))
        self.assertEqual([v[2] for v in changes[:11]], [1, 3, 7, 15, 10, 1, 3, 7, 15, 10, 1])
        for previous, current in zip(changes, changes[1:]):
            duration = current[0] - previous[0]
            self.assertGreaterEqual(duration, 10000)
            self.assertLessEqual(duration, 10020)  # nominal 10 s + at most 2 modeled scans

    def test_08_no_transition_before_ten_seconds(self):
        self.start()
        for _ in range(999):
            self.assertEqual(self.scan().step, 1)
        self.assertEqual(self.scan().step, 2)

    def test_09_each_protective_input_stops_every_step_same_scan(self):
        for step in range(1, 6):
            for field in ("stop_ok", "estop_ok", "water_ok", "overload_ok"):
                with self.subTest(step=step, field=field):
                    plc = ScanModel(state=step, armed=True, saw_off=True, prev_auto=True)
                    out = plc.scan(0, replace(Inputs(auto=True), **{field: False}))
                    self.assertEqual((out.pump, out.mask, out.step), (False, 0, 0))

    def test_10_releasing_stop_does_not_restart(self):
        self.start()
        self.scan(stop_ok=False)
        out = self.scan(stop_ok=True)
        self.assertFalse(out.pump)
        self.assertTrue(out.stop_latched)

    def test_11_reset_in_auto_cannot_restart_or_acknowledge(self):
        self.start()
        self.scan(water_ok=False)
        out = self.scan(water_ok=True, reset=True)
        self.assertFalse(out.pump)
        self.assertEqual(out.fault_bits, 2)

    def test_12_valid_fault_recovery_requires_off_reset_auto(self):
        self.start()
        self.scan(overload_ok=False)
        self.scan(auto=False, overload_ok=True)
        out = self.scan(reset=True)
        self.assertEqual(out.fault_bits, 0)
        self.assertFalse(out.pump)
        self.scan(reset=False)
        self.assertEqual(self.scan(auto=True).step, 1)

    def test_13_stop_recovery_requires_off_reset_auto(self):
        self.start()
        self.scan(stop_ok=False)
        self.scan(stop_ok=True, auto=False)
        out = self.scan(reset=True)
        self.assertFalse(out.stop_latched)
        self.assertFalse(out.pump)
        self.scan(reset=False)
        self.assertTrue(self.scan(auto=True).pump)

    def test_14_reset_while_cause_present_cannot_clear(self):
        self.start()
        self.scan(water_ok=False, auto=False)
        out = self.scan(reset=True)
        self.assertEqual(out.fault_bits, 2)

    def test_15_held_reset_does_not_acknowledge_when_cause_recovers(self):
        self.start()
        self.scan(auto=False, water_ok=False, reset=True)
        out = self.scan(water_ok=True)
        self.assertEqual(out.fault_bits, 2)
        self.scan(reset=False)
        self.assertEqual(self.scan(reset=True).fault_bits, 0)

    def test_16_all_simultaneous_causes_are_retained(self):
        self.start()
        out = self.scan(estop_ok=False, water_ok=False, overload_ok=False, rtc_valid=False, stop_ok=False)
        self.assertEqual(out.fault_bits, 15)
        self.assertTrue(out.stop_latched)
        out = self.scan(estop_ok=True, water_ok=True, overload_ok=True, rtc_valid=True, stop_ok=True)
        self.assertEqual(out.fault_bits, 15)

    def test_17_outside_schedule_stops_every_step_without_fault(self):
        for step in range(1, 6):
            for h, m in ((8, 0), (20, 30)):
                with self.subTest(step=step, h=h, m=m):
                    plc = ScanModel(state=step, armed=True, saw_off=True, prev_auto=True)
                    out = plc.scan(0, Inputs(auto=True, hour=h, minute=m))
                    self.assertEqual((out.pump, out.mask, out.step, out.fault_bits), (False, 0, 0, 0))
                    self.assertTrue(out.armed)

    def test_18_next_schedule_restarts_step_one_without_reset(self):
        self.start()
        self.assertFalse(self.scan(hour=8).pump)
        self.assertFalse(self.scan(hour=16, minute=59).pump)
        out = self.scan(hour=17, minute=0)
        self.assertEqual((out.pump, out.step, out.mask), (True, 1, 1))

    def test_19_select_auto_before_schedule_arms_then_waits(self):
        out = self.scan(auto=True, hour=5, minute=59)
        self.assertTrue(out.armed)
        self.assertFalse(out.pump)
        self.assertTrue(self.scan(hour=6, minute=0).pump)

    def test_20_restart_resets_timers(self):
        self.start()
        for _ in range(700):
            self.scan()
        self.scan(auto=False)
        self.start()
        for _ in range(999):
            self.assertEqual(self.scan().step, 1)

    def test_21_fault_then_toggle_auto_without_reset_cannot_start(self):
        self.start()
        self.scan(water_ok=False)
        self.scan(auto=False, water_ok=True)
        self.assertFalse(self.scan(auto=True).pump)

    def test_22_rtc_failure_latches_and_stops_same_scan(self):
        self.start()
        out = self.scan(rtc_valid=False)
        self.assertEqual((out.pump, out.mask, out.step, out.fault_bits), (False, 0, 0, 8))
        self.assertFalse(self.scan(rtc_valid=True).pump)

    def test_23_first_scan_resets_old_state_and_all_timers(self):
        self.start()
        out = self.scan(first_scan=True)
        self.assertEqual((out.pump, out.mask, out.step), (False, 0, 0))
        self.assertTrue(all(t is None for t in self.plc.timer_start))
        self.assertFalse(self.scan(first_scan=False).pump)

    def test_24_rtc_invalid_in_off_does_not_create_rtc_trip(self):
        out = self.scan(rtc_valid=False)
        self.assertEqual(out.fault_bits, 0)
        self.assertFalse(out.pump)
        self.assertEqual(self.scan(auto=True).fault_bits, 8)

    def test_25_reset_pressed_at_boot_not_a_new_edge(self):
        plc = ScanModel()
        i = Inputs(reset=True, water_ok=False, first_scan=True)
        plc.scan(0, i)
        out = plc.scan(10, replace(i, first_scan=False, water_ok=True))
        self.assertEqual(out.fault_bits, 2)
        plc.scan(20, replace(i, first_scan=False, water_ok=True, reset=False))
        out = plc.scan(30, replace(i, first_scan=False, water_ok=True))
        self.assertEqual(out.fault_bits, 0)

    def test_26_irregular_scan_duration_keeps_required_order(self):
        self.start()
        events = [(self.ms, 1, 1)]
        intervals = [3, 7, 11, 19, 23]
        for k in range(4500):
            self.ms += intervals[k % len(intervals)]
            out = self.plc.scan(self.ms, self.i)
            self.assertTrue(out.pump)
            if out.step != events[-1][1]:
                events.append((self.ms, out.step, out.mask))
        self.assertEqual([e[2] for e in events[:6]], [1, 3, 7, 15, 10, 1])
        for a, b in zip(events, events[1:]):
            self.assertGreaterEqual(b[0] - a[0], 10000)
            self.assertLessEqual(b[0] - a[0], 10046)

    def test_27_all_alarm_combinations_keep_bits_and_summary_priority(self):
        for expected_bits in range(32):
            with self.subTest(alarm_bits=expected_bits):
                plc = ScanModel(armed=True, saw_off=True, prev_auto=True)
                i = Inputs(auto=True, estop_ok=not bool(expected_bits & 1),
                           water_ok=not bool(expected_bits & 2),
                           overload_ok=not bool(expected_bits & 4),
                           rtc_valid=not bool(expected_bits & 8),
                           stop_ok=not bool(expected_bits & 16))
                out = plc.scan(0, i)
                self.assertEqual(out.alarm_bits, expected_bits)
                self.assertEqual(out.fault_bits, expected_bits & 15)
                expected_code = next((code for code, bit in
                                      ((1, 1), (2, 2), (3, 4), (4, 8))
                                      if expected_bits & bit), 0)
                self.assertEqual(out.fault_code, expected_code)

    def test_28_reset_permitted_only_off_with_all_valid_inputs(self):
        self.assertTrue(self.scan().reset_allowed)
        for change in ({"auto": True}, {"stop_ok": False}, {"estop_ok": False},
                       {"water_ok": False}, {"overload_ok": False},
                       {"rtc_valid": False}, {"first_scan": True}):
            with self.subTest(change=change):
                plc = ScanModel()
                self.assertFalse(plc.scan(0, replace(Inputs(), **change)).reset_allowed)

    def test_29_stop_conditions_override_exact_timer_deadline(self):
        for change in ({"auto": False}, {"stop_ok": False}, {"estop_ok": False},
                       {"water_ok": False}, {"overload_ok": False},
                       {"rtc_valid": False}, {"hour": 8}):
            with self.subTest(change=change):
                plc = ScanModel(armed=True, saw_off=True, prev_auto=True)
                initial = Inputs(auto=True)
                self.assertEqual(plc.scan(0, initial).step, 1)
                out = plc.scan(10000, replace(initial, **change))
                self.assertEqual((out.pump, out.mask, out.step), (False, 0, 0))
                self.assertTrue(all(t is None for t in plc.timer_start))

    def test_30_separate_fault_events_accumulate_until_valid_reset(self):
        self.start()
        self.scan(water_ok=False)
        self.scan(water_ok=True)
        out = self.scan(overload_ok=False)
        self.assertEqual((out.fault_bits, out.fault_code, out.alarm_bits), (6, 2, 6))
        out = self.scan(overload_ok=True)
        self.assertEqual(out.alarm_bits, 6)
        self.scan(auto=False)
        out = self.scan(reset=True)
        self.assertEqual((out.alarm_bits, out.fault_code), (0, 0))

    def test_31_random_input_sequences_preserve_output_invariants(self):
        rng = random.Random(40210)
        for _ in range(20000):
            self.ms += rng.randint(1, 25)
            i = Inputs(auto=rng.random() < .8, reset=rng.random() < .1,
                       stop_ok=rng.random() < .98, estop_ok=rng.random() < .99,
                       water_ok=rng.random() < .98, overload_ok=rng.random() < .99,
                       rtc_valid=rng.random() < .99, hour=rng.randrange(24),
                       minute=rng.randrange(60), first_scan=rng.random() < .001)
            out = self.plc.scan(self.ms, i)
            self.assertIn(out.mask, (0, 1, 3, 7, 15, 10))
            self.assertEqual(out.pump, out.mask != 0)
            if out.pump:
                self.assertTrue(i.auto and i.stop_ok and i.estop_ok and i.water_ok
                                and i.overload_ok and i.rtc_valid and out.in_schedule)
                self.assertTrue(out.armed)
                self.assertEqual(out.alarm_bits, 0)
            else:
                self.assertEqual((out.step, out.elapsed_ms), (0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
