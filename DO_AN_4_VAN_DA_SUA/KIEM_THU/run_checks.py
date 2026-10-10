"""Reproduce the independent Python review; never compiles or executes SCL."""
import csv
import hashlib
import io
import json
import platform
import unittest
from dataclasses import replace
from pathlib import Path

from plc_behavior_model import Inputs, ScanModel


ROOT = Path(__file__).resolve().parent
suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_plc_behavior.py")
log = io.StringIO()
result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
header = ("KIEM TRA MO HINH HANH VI PYTHON DOC LAP\n"
          "Khong phai ket qua bien dich SCL / S7-PLCSIM / PLC that.\n"
          f"Python: {platform.python_version()}\n\n")
(ROOT / "TEST_RESULTS.txt").write_text(header + log.getvalue(), encoding="utf-8")

plc = ScanModel()
inputs = Inputs()
out = plc.scan(0, replace(inputs, first_scan=True))
events = [(0, out.step, out.mask, int(out.pump))]
trace = [(0, out.step, out.mask, int(out.pump))]
inputs = replace(inputs, auto=True)
for ms in range(10, 105001, 10):
    out = plc.scan(ms, inputs)
    trace.append((ms, out.step, out.mask, int(out.pump)))
    if out.step != events[-1][1]:
        events.append((ms, out.step, out.mask, int(out.pump)))
with (ROOT / "TRACE_CHUYEN_BUOC.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(("monotonic_ms", "step", "mask_yv1_lsb", "pump_command",
                     "YV1", "YV2", "YV3", "YV4"))
    for ms, step, mask, pump in events:
        writer.writerow((ms, step, mask, pump, *(int(bool(mask & (1 << b))) for b in range(4))))

with (ROOT / "TRACE_2_CHU_KY.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(("monotonic_ms", "step", "mask_yv1_lsb", "pump_command",
                     "YV1", "YV2", "YV3", "YV4"))
    for ms, step, mask, pump in trace:
        writer.writerow((ms, step, mask, pump, *(int(bool(mask & (1 << b))) for b in range(4))))

plc = ScanModel()
with (ROOT / "TRACE_STOP_RESET_AUTO.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(("monotonic_ms", "step", "mask_yv1_lsb", "pump_command",
                     "YV1", "YV2", "YV3", "YV4", "auto", "stop_ok",
                     "reset", "stop_latched", "alarm_bits", "fault_code"))
    for ms in range(0, 105001, 10):
        # STOP 65..66 s; OFF 67..70 s; RESET 68..69 s; AUTO again at 70 s.
        inputs = Inputs(auto=(10 <= ms < 67000 or ms >= 70000),
                        stop_ok=not (65000 <= ms < 66000),
                        reset=(68000 <= ms < 69000), first_scan=(ms == 0))
        out = plc.scan(ms, inputs)
        writer.writerow((ms, out.step, out.mask, int(out.pump),
                         *(int(bool(out.mask & (1 << b))) for b in range(4)),
                         int(inputs.auto), int(inputs.stop_ok), int(inputs.reset),
                         int(out.stop_latched), out.alarm_bits, out.fault_code))

hashes = {}
for path in (ROOT / "plc_behavior_model.py", ROOT / "test_plc_behavior.py",
             ROOT.parent / "PLC" / "Fountain_Auto_4Van.scl"):
    if path.exists():
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
summary = {
    "scope": "Independent Python scan model; not Siemens execution",
    "python": platform.python_version(),
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "successful": result.wasSuccessful(),
    "fixed_scan_ms": 10,
    "event_times_ms": [e[0] for e in events],
    "event_steps": [e[1] for e in events],
    "event_masks": [e[2] for e in events],
    "sha256": hashes,
}
(ROOT / "RUN_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(f"{result.testsRun} tests; failures={len(result.failures)}; errors={len(result.errors)}")
print("Saved TEST_RESULTS.txt, three TRACE_*.csv files, RUN_SUMMARY.json")
raise SystemExit(0 if result.wasSuccessful() else 1)
