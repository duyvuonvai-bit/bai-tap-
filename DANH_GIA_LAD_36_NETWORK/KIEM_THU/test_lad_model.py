"""Behavioral tests against requirement oracles, plus reproduced counterexamples.
Run: python test_lad_model.py
This does not compile or execute code in TIA Portal / PLCSIM.
"""
from dataclasses import replace
from pathlib import Path
import json
import random
import traceback
from lad_model import Inputs, LADModel

OUT = Path(__file__).resolve().parent
RESULTS = []
COUNTEREXAMPLES = {}
REVISIONS = ('original36', 'revised26')
MASKS = {1: 1, 2: 3, 3: 7, 4: 15, 5: 10}

def check(name, fn):
    try:
        evidence = fn()
        RESULTS.append({'name': name, 'passed': True, 'evidence': evidence})
    except Exception as exc:
        RESULTS.append({'name': name, 'passed': False,
                        'error': str(exc), 'traceback': traceback.format_exc()})

def boot(revision, hour=7, minute=0, second=0):
    m = LADModel(revision)
    inp = Inputs(hour=hour, minute=minute, second=second)
    m.scan(inp, 0)
    state = m.scan(replace(inp, auto=True), 10)
    return m, replace(inp, auto=True), 10, state

def must_off(state):
    assert not state['pump'] and state['mask'] == 0, state

def schedule_oracle(seconds):
    return 6*3600 <= seconds < 8*3600 or 17*3600 <= seconds < 20*3600+30*60

def schedule_all(rev, step_seconds):
    model = LADModel(rev)
    count = 0
    for index, sec in enumerate(range(0, 86400, step_seconds)):
        state = model.scan(Inputs(hour=sec//3600, minute=sec%3600//60,
                                  second=sec%60), index*10)
        assert state['in_schedule'] == schedule_oracle(sec), (sec, state)
        count += state['in_schedule']
    assert count*step_seconds == 19800
    return {'sampled_times': 86400//step_seconds, 'operating_seconds': 19800,
            'boundary_rule': 'start included, end excluded'}

for rev in REVISIONS:
    check(f'{rev}: all 1440 minutes', lambda r=rev: schedule_all(r, 60))
    check(f'{rev}: every second of 24-hour day', lambda r=rev: schedule_all(r, 1))

def startup(rev):
    m = LADModel(rev)
    for t in range(0, 100, 10):
        state = m.scan(Inputs(auto=True), t)
        must_off(state)
        assert not state['armed']
    m.scan(Inputs(auto=False), 100)
    state = m.scan(Inputs(auto=True), 110)
    assert state['step'] == 1 and state['mask'] == 1 and state['pump']
    return 'AUTO at startup blocked; fresh OFF→AUTO starts at step 1'

for rev in REVISIONS:
    check(f'{rev}: startup AUTO cannot self-start', lambda r=rev: startup(r))

def sequence(rev, scan_ms):
    m, inp, t, state = boot(rev)
    old_step = 1
    entered = t
    durations = []
    transitions = []
    samples = 0
    while len(transitions) < 10:
        t += scan_ms
        state = m.scan(inp, t)
        samples += 1
        assert state['run'] and state['pump'] and not state['alarm'], state
        assert state['mask'] == MASKS[state['step']], state
        if state['step'] != old_step:
            assert state['step'] == old_step%5+1, state
            duration = t-entered
            assert duration >= 10_000, (duration, state)
            assert duration <= 10_000+2*scan_ms, (duration, scan_ms)
            durations.append(duration)
            transitions.append([old_step, state['step']])
            entered, old_step = t, state['step']
    return {'scan_ms': scan_ms, 'samples': samples,
            'transitions': transitions, 'step_durations_ms': durations,
            'pump_command_continuous': True,
            'note': 'TON starts on first scan that observes committed new step'}

for rev in REVISIONS:
    for scan_ms in (1, 10, 37):
        check(f'{rev}: 2 cycles, masks, no early transition, scan {scan_ms}ms',
              lambda r=rev, s=scan_ms: sequence(r, s))

def find_step(rev, step):
    m, inp, t, state = boot(rev)
    while state['step'] != step:
        t += 10
        state = m.scan(inp, t)
    return m, inp, t, state

def stop_everywhere(rev):
    cases = []
    for step in range(1, 6):
        for signal in ('water', 'estop_ok', 'overload_ok', 'stop_ok'):
            m, inp, t, _ = find_step(rev, step)
            trip = m.scan(replace(inp, **{signal: False}), t+10)
            must_off(trip)
            assert not trip['run'] and trip['step'] == 0
            assert trip['stop_latched'] if signal == 'stop_ok' else trip['fault_latched']
            restored = m.scan(inp, t+20)
            must_off(restored)
            assert not restored['armed']
            # RESET while AUTO is still selected cannot acknowledge.
            ignored = m.scan(replace(inp, reset=True), t+30)
            must_off(ignored)
            assert not ignored['ack']
            m.scan(replace(inp, auto=False, reset=False), t+40)
            acknowledged = m.scan(replace(inp, auto=False, reset=True), t+50)
            must_off(acknowledged)
            assert acknowledged['ack']
            restart = m.scan(inp, t+60)
            assert restart['step'] == 1 and restart['mask'] == 1 and restart['pump']
            cases.append({'step': step, 'trip_input': signal,
                          'same_scan_stop': True, 'restart_requires_off_reset_auto': True})
    return cases

for rev in REVISIONS:
    check(f'{rev}: four stop inputs at all five steps', lambda r=rev: stop_everywhere(r))

def held_reset(rev):
    m, inp, t, _ = boot(rev)
    m.scan(replace(inp, water=False), t+10)
    m.scan(replace(inp, auto=False, water=False, reset=True), t+20)
    still_fault = m.scan(replace(inp, auto=False, reset=True), t+30)
    assert still_fault['fault_latched'] and not still_fault['ack']
    attempt = m.scan(replace(inp, reset=True), t+40)
    must_off(attempt)
    m.scan(replace(inp, auto=False, reset=False), t+50)
    ack = m.scan(replace(inp, auto=False, reset=True), t+60)
    assert ack['ack'] and not ack['fault_latched']
    restarted = m.scan(inp, t+70)
    assert restarted['pump']
    return 'Held RESET cannot acknowledge when water returns; release and press required'

for rev in REVISIONS:
    check(f'{rev}: held RESET through recovery', lambda r=rev: held_reset(r))

def ordinary_off(rev):
    m, inp, t, _ = find_step(rev, 4)
    off = m.scan(replace(inp, auto=False), t+10)
    must_off(off)
    assert not off['fault_latched'] and not off['stop_latched']
    on = m.scan(inp, t+20)
    assert on['step'] == 1 and on['pump']
    return 'Normal OFF→AUTO needs no RESET and restarts step 1'

for rev in REVISIONS:
    check(f'{rev}: normal OFF/ON', lambda r=rev: ordinary_off(r))

def across_shifts(rev):
    m, inp, t, state = boot(rev, 5, 59, 59)
    must_off(state)
    assert state['armed']
    six = m.scan(replace(inp, hour=6, minute=0, second=0), t+10)
    assert six['pump'] and six['step'] == 1
    eight = m.scan(replace(inp, hour=8, minute=0, second=0), t+20)
    must_off(eight)
    assert eight['armed'] and not eight['alarm']
    fivepm = m.scan(replace(inp, hour=17, minute=0, second=0), t+30)
    assert fivepm['pump'] and fivepm['step'] == 1
    end = m.scan(replace(inp, hour=20, minute=30, second=0), t+40)
    must_off(end)
    assert end['armed'] and not end['alarm']
    return 'Scheduled stop preserves AUTO permission for next shift; no alarm'

for rev in REVISIONS:
    check(f'{rev}: automatic next scheduled shift', lambda r=rev: across_shifts(r))

def rtc_recovery(rev):
    m, inp, t, _ = boot(rev)
    failed = m.scan(replace(inp, rtc_status=-32768), t+10)
    must_off(failed)
    assert failed['alarm'] and not failed['armed']
    recovered = m.scan(inp, t+20)
    must_off(recovered)
    m.scan(replace(inp, auto=False), t+30)
    tried_auto = m.scan(inp, t+40)
    if rev == 'original36':
        assert tried_auto['pump'] and not tried_auto['alarm']
        return 'Original policy: RTC recovery requires OFF→AUTO; RESET not required'
    must_off(tried_auto)
    assert tried_auto['fault_latched']
    m.scan(replace(inp, auto=False), t+50)
    ack = m.scan(replace(inp, auto=False, reset=True), t+60)
    assert ack['ack']
    restarted = m.scan(inp, t+70)
    assert restarted['pump']
    return 'Added policy: RTC fault latched, requires OFF→RESET→AUTO'

for rev in REVISIONS:
    check(f'{rev}: RTC error and recovery policy', lambda r=rev: rtc_recovery(r))

def corrupt_step(rev):
    cases = []
    for corrupt in (-1, 6, 100, 32767):
        m, inp, t, _ = boot(rev)
        m.step = corrupt
        state = m.scan(inp, t+10)
        must_off(state)
        if rev == 'original36':
            assert state['run'] and state['step'] == corrupt and not state['alarm']
        else:
            assert not state['run'] and state['step'] == 0 and state['alarm']
            m.scan(replace(inp, auto=False), t+20)
            ack = m.scan(replace(inp, auto=False, reset=True), t+30)
            assert ack['ack'] and not ack['alarm']
            restarted = m.scan(inp, t+40)
            assert restarted['pump'] and restarted['step'] == 1
        cases.append({'injected_step': corrupt, 'observed': state})
    COUNTEREXAMPLES[rev + '_invalid_step'] = cases
    return {'injections': [-1, 6, 100, 32767],
            'original_outcome': 'Silent stall, Run remains TRUE, outputs OFF, no alarm',
            'revised_outcome': 'Fault latched, Run FALSE, step zero, outputs OFF',
            'assessed_revision': rev}

for rev in REVISIONS:
    check(f'{rev}: invalid-step injection and diagnosis', lambda r=rev: corrupt_step(r))

def stop_at_timer_expiry(rev):
    m, inp, t, _ = boot(rev)
    m.scan(inp, t+10)  # Timer1 starts.
    state = m.scan(replace(inp, stop_ok=False), t+10010)
    must_off(state)
    assert state['step'] == 0 and not any(state['timer_done'])
    return 'STOP has priority when timer would expire; no stale timer transition'

for rev in REVISIONS:
    check(f'{rev}: STOP at timer expiry', lambda r=rev: stop_at_timer_expiry(r))

def rtc_status_one():
    states = {}
    for rev in REVISIONS:
        m = LADModel(rev)
        m.scan(Inputs(rtc_status=1), 0)
        states[rev] = m.scan(Inputs(auto=True, rtc_status=1), 10)
    must_off(states['original36'])
    assert states['revised26']['pump'] and states['revised26']['rtc_ok']
    COUNTEREXAMPLES['dst_status_one'] = states
    return 'Revision accepts documented status 1; Vietnam normally uses 0 because DST is disabled'

check('RD_LOC_T success status 1 with DST', rtc_status_one)

def invalid_time_fields():
    cases = [Inputs(auto=True, hour=24), Inputs(auto=True, minute=60),
             Inputs(auto=True, second=60)]
    for inp in cases:
        m, _, t, _ = boot('revised26')
        state = m.scan(inp, t+10)
        must_off(state)
        assert not state['rtc_ok'] and state['alarm']
    return 'Out-of-range HOUR/MINUTE/SECOND stops and diagnoses when AUTO is selected'

check('revised26: DTL field bounds', invalid_time_fields)

def first_scan_reset_held():
    m = LADModel('revised26')
    state = m.scan(Inputs(auto=False, reset=True), 0)
    assert state['first_scan'] and not state['reset_edge'] and not state['ack']
    second = m.scan(Inputs(auto=False, reset=True), 10)
    assert not second['reset_edge'] and not second['ack']
    m.scan(Inputs(auto=False, reset=False), 20)
    newpress = m.scan(Inputs(auto=False, reset=True), 30)
    assert newpress['reset_edge'] and newpress['ack']
    return 'Startup-held RESET is ignored until released and pressed again'

check('revised26: first-scan edge suppression', first_scan_reset_held)

def random_invariants(rev):
    rng = random.Random(20261011)
    m, inp, t, _ = boot(rev)
    n = 15000
    for _ in range(n):
        t += rng.choice((1, 7, 10, 37, 100, 1000))
        if rng.random() < .03:
            field = rng.choice(('auto','water','reset','estop_ok','overload_ok','stop_ok'))
            inp = replace(inp, **{field:not getattr(inp,field)})
        if rng.random() < .01:
            inp = replace(inp, hour=rng.randrange(24), minute=rng.randrange(60))
        if rng.random() < .005:
            inp = replace(inp, rtc_status=rng.choice((0,0,0,-32768)))
        state = m.scan(inp, t)
        if not state['run']:
            must_off(state)
            assert state['step'] == 0
        if state['pump']:
            assert state['run'] and state['safe'] and state['in_schedule']
            assert not state['fault_latched'] and not state['stop_latched']
            assert state['mask'] == MASKS[state['step']]
        if not inp.auto or not state['safe'] or not state['rtc_ok']:
            must_off(state)
    return {'seed': 20261011, 'scans': n, 'scope': 'Reachable state/input invariants, no claim of exhaustive proof'}

for rev in REVISIONS:
    check(f'{rev}: randomized scan invariants', lambda r=rev: random_invariants(r))

passed = sum(r['passed'] for r in RESULTS)
summary = {
    'scope': 'Independent Python model of scan-order logic, not TIA compilation or PLCSIM/hardware test',
    'assumptions': [
        'Each R_TRIG is called every scan with its own state',
        'All five independent TONs are called every scan; IN false resets',
        'Non-retentive startup values follow documentation; revised model adds first-scan handling',
        'Healthy-high field inputs; process-image values stable within a scan',
        'Monotonic timer time is independent of RTC schedule',
        'Original model follows illustrative images, not unseen native PLC project'],
    'total_cases': len(RESULTS), 'passed': passed, 'failed': len(RESULTS)-passed,
    'original_logic_defect_reproduced': 'Out-of-range step yields silent stall; is not dangerous energized output in this model',
    'policy_difference': 'Revised RTC fault in AUTO is latched and requires RESET while OFF; original only requires OFF→AUTO after RTC recovers',
    'results': RESULTS}
(OUT/'ket_qua_kiem_thu.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
(OUT/'counterexamples.json').write_text(json.dumps(COUNTEREXAMPLES, ensure_ascii=False, indent=2)+'\n')
print(f'{passed}/{len(RESULTS)} cases passed; {len(RESULTS)-passed} failed')
if passed != len(RESULTS):
    for result in RESULTS:
        if not result['passed']:
            print(result['name'], result['error'])
    raise SystemExit(1)
