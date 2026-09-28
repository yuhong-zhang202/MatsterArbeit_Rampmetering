#!/usr/bin/env python3
"""BUILD01-only approval-bound launcher. Import/preflight never starts a binary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering')
BASE = ROOT / 'artifacts/stage6_recovery_p2_revision_01/engineering'
OUTPUT = BASE / 'build_attempts/BUILD01'
BINARY = Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/netconvert')
BINARY_SHA = '919f8491518379daeaf2e215a96e58edb4bed4894cbf6ef948788170d5bea9b5'
SUMO_HOME = '/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo'
LIMITS = dict(GUI=0, SUMO=0, TraCI=0, netconvert_starts=1, technical_retry=0, total_output_bytes=100000000, wallclock_s=30)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_symlink(path):
    path = Path(path)
    require(path.is_absolute(), 'Path must be absolute')
    for component in (path, *path.parents):
        require(not component.is_symlink(), 'Symlink rejected: ' + str(component))


def verify_binding(binding):
    path = Path(binding['path'])
    no_symlink(path)
    require(path.is_file(), 'Missing bound file: ' + str(path))
    require(path.stat().st_size == binding['bytes'], 'Size mismatch: ' + str(path))
    require(digest(path) == binding['sha256'], 'Hash mismatch: ' + str(path))


def check_approval(card_path, approval_path):
    no_symlink(card_path)
    no_symlink(approval_path)
    require(Path(card_path) != Path(approval_path), 'Independent sidecar required')
    approval = json.loads(Path(approval_path).read_text())
    require(approval.get('status') == 'user-approved', 'No explicit approval')
    require(approval.get('synthetic_test_only') is False, 'Synthetic approval forbidden')
    require(approval.get('scope') == 'SG6-BUILD BUILD01 only', 'Wrong approval scope')
    require(approval.get('card_sha256') == digest(card_path), 'Approval card SHA mismatch')
    require(approval.get('card_path') == str(card_path), 'Approval card path mismatch')
    require(approval.get('max_netconvert_starts') == 1, 'Wrong approval budget')
    require(approval.get('monitoring_semantics') == 'polling_50ms_possible_overshoot_preserved', 'Monitoring semantics not acknowledged')
    require(bool(approval.get('user_approval_quote')) and bool(approval.get('approved_at')), 'Missing human authorization provenance')
    return approval


def validate_card(card_path, approval_path, environment):
    card = json.loads(Path(card_path).read_text())
    require(card.get('kind') == 'SG6_BUILD_REQUEST_FINAL_OFFLINE', 'Not final BUILD card')
    require(card.get('attempt_id') == 'BUILD01', 'Only BUILD01 supported')
    require(card.get('approved') is False and card.get('authorized_starts') == 0, 'Card must remain inactive; approval lives in sidecar')
    require(card.get('proposed_limits') == LIMITS, 'Limits changed')
    require(card.get('argv') == [str(BINARY), '-c', str(BASE / 'network_inputs/candidate.schema_revision02.netccfg')], 'Wrong command')
    require(card.get('cwd') == str(ROOT), 'Wrong cwd')
    require(card.get('output_dir') == str(OUTPUT), 'Wrong BUILD01 directory')
    require(card.get('network_output') == str(OUTPUT / 'network.net.xml'), 'Wrong network output')
    for key, name in [('stdout_path','netconvert.stdout.log'),('stderr_path','netconvert.stderr.log'),('receipt_path','build_receipt.json')]:
        require(card.get(key) == str(OUTPUT / name), 'Wrong ' + key)
    no_symlink(OUTPUT)
    require(not OUTPUT.exists(), 'BUILD01 already claimed; consumed, no automatic retry')
    require(card.get('environment_overrides') == {'SUMO_HOME': SUMO_HOME}, 'Wrong SUMO_HOME binding')
    require(environment.get('SUMO_HOME') == SUMO_HOME, 'Calling SUMO_HOME must exactly match')
    require(not any(k.startswith(('DYLD_', 'LD_')) for k in environment), 'Dynamic-loader overrides rejected')
    require(card['binary']['path'] == str(BINARY) and card['binary']['sha256'] == BINARY_SHA, 'Wrong binary binding')
    required_inputs = {str(BASE / 'network_inputs' / x) for x in ['candidate.con.xml','candidate.edg.xml','candidate.schema_revision02.netccfg','candidate.nod.xml','candidate.tll.xml']}
    require({x['path'] for x in card['inputs']} == required_inputs and len(card['inputs']) == 5, 'Incomplete input binding')
    require(len(card['schema_bindings']) == 23, 'Incomplete schema bindings')
    require(card['project_cumulative_budget']['status'] == 'reconciled_with_explicit_exclusions', 'Cumulative audit pending')
    contract = card['execution_contract']
    require(contract['executor']['path'] == str(Path(__file__).absolute()), 'Wrong executor')
    require(contract['watchdog_poll_s'] == 0.05 and contract['termination_grace_s'] == 1, 'Watchdog contract changed')
    for binding in [card['binary'], card['binding_manifest'], *card['inputs'], *card['schema_bindings'], contract['executor'], contract['test_receipt'], contract['test_script'], contract['contract_document'], card['project_cumulative_budget']['evidence']]:
        verify_binding(binding)
    test_receipt = json.loads(Path(contract['test_receipt']['path']).read_text())
    require(test_receipt.get('status') == 'PASS' and test_receipt.get('real_simulator_starts') == 0, 'Executor tests absent or failed')
    require(test_receipt.get('executor_sha256') == digest(__file__), 'Tests bind another executor')
    config = ET.parse(card['argv'][2]).getroot()
    require(config.find('output/output-file').get('value') == str(OUTPUT / 'network.net.xml'), 'Config output differs')
    for tag, suffix in [('node-files','nod'),('edge-files','edg'),('connection-files','con'),('tllogic-files','tll')]:
        require(config.find('input/' + tag).get('value') == str(BASE / ('network_inputs/candidate.' + suffix + '.xml')), 'Config source differs')
    approval = check_approval(card_path, approval_path)
    return card, approval


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def durable_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    fsync_dir(Path(path).parent)


def directory_bytes(path):
    total = 0
    for root, dirs, names in os.walk(path, followlinks=False):
        for name in dirs + names:
            item = Path(root) / name
            require(not item.is_symlink(), 'Output symlink rejected')
            if item.is_file():
                total += item.stat().st_size
    return total


def terminate_group(process):
    # A new session makes pid the dedicated process-group id. Never signal self.
    require(process.pid != os.getpid() and process.pid > 1, 'Unsafe process group')
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=1)
            return
        except subprocess.TimeoutExpired:
            continue
    raise RuntimeError('Cannot confirm child termination; manual intervention required')


def _run_reserved(output, argv, cwd, env, approval_record, factory=subprocess.Popen,
                  clock=time.monotonic, sleep=time.sleep, size_fn=directory_bytes,
                  terminate=terminate_group, timeout=30, cap=100000000, synthetic=False):
    """Private testable core. Production caller fixes all arguments after preflight."""
    output = Path(output)
    no_symlink(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    os.mkdir(output)  # Exclusive claim: even an empty orphan claim consumes BUILD01.
    fsync_dir(output.parent)
    reservation = dict(attempt_id='BUILD01', reserved_starts=1, consumed_starts=1,
                       automatic_retry=False, synthetic_test_only=synthetic,
                       argv=argv, approval=approval_record, reserved_at=time.time(),
                       crash_rule='Any claimed directory without terminal receipt is terminal_unknown_consumed; never relaunch')
    durable_json(output / 'reservation.json', reservation)
    start = clock()
    process = None
    status = 'terminal_start_failure'
    error = None
    peak = 0
    returncode = None
    terminated = False
    try:
        with (output / 'netconvert.stdout.log').open('xb', buffering=0) as stdout, (output / 'netconvert.stderr.log').open('xb', buffering=0) as stderr:
            process = factory(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            durable_json(output / 'started.json', dict(pid=process.pid, wallclock_started=time.time(), synthetic_test_only=synthetic))
            while True:
                peak = max(peak, size_fn(output))
                returncode = process.poll()
                if peak > cap:
                    status = 'terminal_output_envelope_exceeded'
                    break
                if clock() - start >= timeout:
                    status = 'terminal_timeout'
                    break
                if returncode is not None:
                    status = 'completed_pending_compiled_review' if returncode == 0 else 'terminal_nonzero'
                    break
                sleep(0.05)
            if status in ('terminal_timeout', 'terminal_output_envelope_exceeded'):
                terminate(process)
                terminated = True
                returncode = process.poll()
            stdout.flush()
            stderr.flush()
            os.fsync(stdout.fileno())
            os.fsync(stderr.fileno())
    except BaseException as exc:
        error = type(exc).__name__ + ': ' + str(exc)
        status = 'terminal_executor_exception' if process is not None else 'terminal_start_failure'
        if process is not None:
            try:
                terminate(process)
                terminated = True
            except BaseException as termination_error:
                error += '; termination unknown: ' + repr(termination_error)
                status = 'terminal_termination_unknown_consumed'
    try:
        peak = max(peak, size_fn(output))
    except BaseException as exc:
        status = 'terminal_output_inspection_failure'
        error = repr(exc)
    if peak > cap:
        status = 'terminal_output_envelope_exceeded'
    network = output / 'network.net.xml'
    if status == 'completed_pending_compiled_review':
        try:
            require(network.is_file() and network.stat().st_size > 0, 'Missing compiled network')
            require(ET.parse(network).getroot().tag == 'net', 'Wrong network XML root')
        except BaseException as exc:
            status = 'terminal_missing_or_invalid_network'
            error = repr(exc)
    receipt = dict(status=status, consumed_starts=1, automatic_retry=False,
                   synthetic_test_only=synthetic, returncode=returncode,
                   wallclock_s=clock()-start, observed_peak_bytes=peak,
                   monitored_cap_bytes=cap, monitored_timeout_s=timeout,
                   polling_overshoot_possible=True, termination_requested=terminated,
                   error=error, approval=approval_record,
                   stderr_nonempty=(output/'netconvert.stderr.log').exists() and (output/'netconvert.stderr.log').stat().st_size > 0,
                   outputs={p.name:dict(bytes=p.stat().st_size,sha256=digest(p)) for p in output.iterdir() if p.is_file() and not p.is_symlink()},
                   scientific_acceptance=False, compiled_guard_acceptance=False)
    # This terminal receipt is outside the simulator's output budget accounting at final write;
    # final exact total is printed and any overrun remains a failure, never deleted.
    durable_json(output / 'build_receipt.json', receipt)
    final_bytes = directory_bytes(output)
    if final_bytes > cap and status != 'terminal_output_envelope_exceeded':
        durable_json(output / 'final_envelope_violation.json', dict(status='terminal_output_envelope_exceeded', exact_bytes_before_this_record=final_bytes, consumed_starts=1, automatic_retry=False))
        receipt['status'] = 'terminal_output_envelope_exceeded'
    receipt['final_directory_bytes'] = directory_bytes(output)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--card', type=Path, required=True)
    parser.add_argument('--approval', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps(dict(status='DRY_RUN_NO_PROCESS', card_sha256=digest(args.card), approval_required=True, starts=0)))
        return 0
    require(args.approval is not None, 'Independent approval sidecar required')
    card, approval = validate_card(args.card.absolute(), args.approval.absolute(), os.environ)
    approval_record = dict(card_path=str(args.card.absolute()), card_sha256=digest(args.card), sidecar_path=str(args.approval.absolute()), sidecar_sha256=digest(args.approval), approval=approval)
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Termination signal ' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGHUP, interrupted)
    # A clean environment prevents unrelated caller settings changing the binary behavior.
    env = dict(SUMO_HOME=SUMO_HOME, PATH='/usr/bin:/bin', LC_ALL='C', LANG='C', HOME=os.environ.get('HOME',''))
    result = _run_reserved(OUTPUT, card['argv'], str(ROOT), env, approval_record)
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] == 'completed_pending_compiled_review' else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('FAIL_CLOSED: ' + repr(exc), file=sys.stderr)
        sys.exit(2)
