"""Audited, pristine-only recovery. No resume, permit, build or budget reset."""
import base64
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
ROOT = Path('/home/evan-williams/deeph-m9')
AUDITS = PROJECT / '08_audits'
SELF = PROJECT / '06_reproduction/controllers/m9_source_build_mpi_recovery_v1.py'
ADAPTER = PROJECT / '06_reproduction/controllers/m9_openmx_mpi_repair_v1.py'
TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_mpi_recovery_v1.py'
ADAPTER_TEST = PROJECT / '06_reproduction/tests/test_m9_openmx_mpi_repair_v1.py'
WORK = AUDITS / 'M9_source_build_mpi_recovery_v1_work_package.md'
AUTH = AUDITS / 'M9_source_build_mpi_recovery_v1_user_authorization.md'
FROZEN = PROJECT / '06_reproduction/manifests/m9_source_build_mpi_recovery_v1_frozen_hashes.json'
REPORT = AUDITS / 'M9_source_build_mpi_recovery_v1_implementation_audit.md'
VERDICT = AUDITS / 'M9_source_build_mpi_recovery_v1_implementation_verdict.json'
BASELINE = AUDITS / 'M9_source_build_v2_postexecution_evidence.json'
BASELINE_SHA = 'e6f02744745837ae200998cf6d1e7701283721e8ed64c550e98d58b416f5f325'
FAIL_REPORT = AUDITS / 'M9_source_build_v2_execution_independent_audit.md'
FAIL_REPORT_SHA = '2bcf74043ae31d6cbe5e7165be139b0d7056f90a80451fb31cc1d5deed727829'
OLD_CONSUMER = PROJECT / '06_reproduction/controllers/m9_source_build_v2_consumer.py'
OLD_CONSUMER_SHA = '1b425c04d98549a7a9a5ea502411379e36bee3968a0eec66f205796a222e36e4'
PRIVATE = Path('/root/deeph-m9-control/source-build-mpi-recovery-v1')
SNAPSHOT = ROOT / 'controls/source-build-mpi-repair-v1'
JOURNAL = PRIVATE / 'journal.json'
LOCK = ROOT / 'manifests/budget.lock'
STATE = ROOT / 'manifests/budget_state.json'
WORKFLOW = ROOT / 'manifests/overlap_workflow_state.json'
LEDGER = ROOT / 'manifests/budget_ledger.jsonl'
TX = ROOT / 'manifests/overlap_transaction.json'
RECOVERY_ID = 'm9-source-build-mpi-recovery-20260831-01'
FAILURE_ID = '38a891fff6fd07675581b891766e02c6'
PHASES = ('PREPARED', 'SNAPSHOT_COMMITTED', 'LEDGER_COMMITTED',
          'STATE_COMMITTED', 'WORKFLOW_COMMITTED', 'SUCCESS_COMMITTED')
SOURCE_SET = {SELF, ADAPTER, TEST, ADAPTER_TEST, WORK, AUTH, BASELINE, FAIL_REPORT, OLD_CONSUMER}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def pinned(path, digest):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        a = os.fstat(fd)
        with os.fdopen(os.dup(fd), 'rb') as stream:
            data = stream.read()
        b, linked = os.fstat(fd), os.lstat(path)
        keys = ('st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if (not stat.S_ISREG(a.st_mode) or a.st_nlink != 1 or len(data) != a.st_size
                or any(getattr(a, k) != getattr(b, k) or getattr(b, k) != getattr(linked, k) for k in keys)
                or digest is not None and sha(data) != digest):
            raise ValueError('recovery pinned source differs: ' + str(path))
        return data
    finally:
        os.close(fd)


def load_source(name, path, raw):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def authority(args):
    if len(args) != 5 or args[1] not in ('preflight', 'recover'):
        raise ValueError('expected self_sha preflight|recover frozen_sha verdict_sha report_sha; no resume')
    self_sha, _, frozen_sha, verdict_sha, report_sha = args
    payloads = {FROZEN: pinned(FROZEN, frozen_sha), REPORT: pinned(REPORT, report_sha),
                VERDICT: pinned(VERDICT, verdict_sha)}
    frozen = json.loads(payloads[FROZEN])
    if set(frozen) != {'schema', 'files'} or frozen['schema'] != 'm9-mpi-recovery-frozen-v1' or set(frozen['files']) != {str(p) for p in SOURCE_SET}:
        raise ValueError('recovery source closure differs')
    for name, digest in frozen['files'].items():
        payloads[Path(name)] = pinned(Path(name), digest)
    if (frozen['files'][str(SELF)] != self_sha or sha(payloads[BASELINE]) != BASELINE_SHA
            or sha(payloads[FAIL_REPORT]) != FAIL_REPORT_SHA or sha(payloads[OLD_CONSUMER]) != OLD_CONSUMER_SHA):
        raise ValueError('recovery historical authority differs')
    verdict = json.loads(payloads[VERDICT])
    expected = {'schema': 'm9-mpi-recovery-verdict-v1', 'status': 'PASS', 'blocking': 0,
                'non_blocking': 0, 'frozen_sha256': frozen_sha,
                'report_path': str(REPORT), 'report_sha256': report_sha}
    if (verdict != expected or type(verdict['blocking']) is not int or type(verdict['non_blocking']) is not int):
        raise ValueError('recovery independent authority must be exact PASS/0/0')
    c = load_source('m9_mpi_recovery_old_consumer', OLD_CONSUMER, payloads[OLD_CONSUMER])
    c.verify_sources(json.loads(c.read_bytes(c.FROZEN, 'bc80d1d939527818c7eec747a60cd17c6000f9015374ff33192f34c2f3ae7614')))
    repair = load_source('m9_mpi_recovery_adapter', ADAPTER, payloads[ADAPTER])
    repair.derive(repair.pinned(repair.BASE, repair.BASE_SHA))
    return payloads, c, repair


def capture(reader):
    result = {}
    for path in (ROOT / 'manifests', ROOT / 'controls', PRIVATE.parent):
        result.update(reader.capture_tree(path))
    return result


def baseline_raw(baseline):
    result = {}
    for path, item in baseline['runtime_raw_bytes'].items():
        raw = base64.b64decode(item['base64'], validate=True)
        if sha(raw) != item['sha256'] or len(raw) != item['bytes']:
            raise ValueError('baseline raw runtime differs')
        result[Path(path)] = raw
    if set(result) != {STATE, WORKFLOW, LEDGER, TX}:
        raise ValueError('baseline runtime closure differs')
    return result


def require_idle(baseline):
    cap = baseline['capability']
    expected = [b'\0'.join(x.encode() for x in cap[field]) + b'\0'
                for field in ('budget_argv', 'launcher_argv')]
    for directory in Path('/proc').iterdir():
        if directory.name.isdecimal():
            try:
                raw = (directory / 'cmdline').read_bytes()
            except (FileNotFoundError, ProcessLookupError):
                continue
            if raw in expected:
                raise ValueError('historical budget or launcher still alive')


def require_pristine():
    for path in (PRIVATE, SNAPSHOT, SNAPSHOT.with_name(SNAPSHOT.name + '.staging'),
                 STATE.with_name(STATE.name + '.mpi-recovery.tmp'),
                 WORKFLOW.with_name(WORKFLOW.name + '.mpi-recovery.tmp')):
        if os.path.lexists(path):
            raise ValueError('non-pristine recovery; preserve and stop: ' + str(path))


def targets(raw, utc, bindings):
    state, workflow, tx = (json.loads(raw[p]) for p in (STATE, WORKFLOW, TX))
    if (state['hard_stopped'] is not True or workflow['hard_stopped'] is not True
            or workflow['stage'] != 'HARD_STOP' or tx['state'] != 'FAILED_COMMITTED'
            or tx['transaction_id'] != FAILURE_ID or tx['action'] != 'source_build'
            or tx['reasons'] != ['overlap_command_failed'] or tx['timed_out'] is not False
            or tx['exit_code'] != 1 or state['active_overlap_transaction'] is not None
            or workflow['active_transaction'] is not None):
        raise ValueError('recovery failure semantics differ')
    state['hard_stopped'] = False
    state['last_event_utc'] = utc
    state['recovered_from_source_build_mpi_failure'] = RECOVERY_ID
    workflow['hard_stopped'] = False
    workflow['stage'] = 'SOURCES_PREPARED'
    workflow['recovered_from_source_build_mpi_failure'] = RECOVERY_ID
    event = {'event': 'SOURCE_BUILD_MPI_RECOVERY', 'event_id': RECOVERY_ID, 'utc': utc,
             'parent_transaction_id': FAILURE_ID, 'parent_transaction_sha256': sha(raw[TX]),
             'ledger_prefix_sha256': sha(raw[LEDGER]), 'ledger_prefix_bytes': len(raw[LEDGER]),
             'cpu_seconds': state['cpu_seconds'], 'gpu_seconds': state['gpu_seconds'],
             'cpu_adjustments': state['cpu_adjustments'], 'authorization': bindings,
             'source_build_authorized': False}
    line = (json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n').encode()
    return {STATE: encode(state), WORKFLOW: encode(workflow), LEDGER: raw[LEDGER] + line}, event, line


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_all(fd, raw):
    offset = 0
    while offset < len(raw):
        count = os.write(fd, raw[offset:])
        if count <= 0:
            raise OSError('short recovery write')
        offset += count


class Guard:
    def __init__(self, reader, expected, lock_fd):
        self.reader, self.expected, self.lock_fd = reader, dict(expected), lock_fd

    def lock(self):
        actual = self.reader.filesystem_receipt(LOCK)
        if actual != self.expected[str(LOCK)]:
            raise ValueError('recovery lock path identity drift')
        stat_fd = os.fstat(self.lock_fd)
        if (stat_fd.st_dev, stat_fd.st_ino) != (actual['dev'], actual['ino']):
            raise ValueError('recovery lock descriptor drift')

    def check(self):
        self.lock()
        if capture(self.reader) != self.expected:
            raise ValueError('recovery phase namespace/identity drift')

    def parent(self, path, nlink_delta=0):
        before, after = self.expected[str(path)], self.reader.filesystem_receipt(path)
        wanted = dict(before); wanted['nlink'] += nlink_delta
        fields = {'bytes', 'mtime_ns', 'ctime_ns'}
        if {k:v for k,v in wanted.items() if k not in fields} != {k:v for k,v in after.items() if k not in fields}:
            raise ValueError('recovery parent security drift')
        self.expected[str(path)] = after

    def directory(self, path, gid):
        self.check()
        if os.path.lexists(path):
            raise ValueError('recovery directory exists')
        os.mkdir(path, 0o700); os.chown(path, 0, gid); os.chmod(path, 0o700)
        self.expected[str(path)] = self.reader.filesystem_receipt(path)
        self.parent(path.parent, 1)
        sync_dir(path.parent)
        self.check()

    def file(self, path, raw, uid=0, gid=0, mode=0o600, replace=False):
        self.check()
        if not replace and os.path.lexists(path):
            raise ValueError('recovery new file already exists')
        if replace and str(path) not in self.expected:
            raise ValueError('unbound recovery replace')
        temporary = path.with_name(path.name + '.mpi-recovery.tmp') if replace else path
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, mode)
        try:
            os.fchown(fd, uid, gid); os.fchmod(fd, mode)
            write_all(fd, raw); os.fsync(fd)
            created = os.fstat(fd)
        finally:
            os.close(fd)
        if replace:
            if self.reader.filesystem_receipt(path) != self.expected[str(path)]:
                raise ValueError('target changed before replacement')
            os.replace(temporary, path)
        receipt = self.reader.filesystem_receipt(path)
        if ((receipt['dev'], receipt['ino']) != (created.st_dev, created.st_ino)
                or receipt['sha256'] != sha(raw) or receipt['bytes'] != len(raw)
                or (receipt['uid'], receipt['gid'], receipt['mode'], receipt['nlink']) != (uid, gid, mode, 1)):
            raise ValueError('recovery written receipt differs')
        self.expected[str(path)] = receipt
        self.parent(path.parent)
        sync_dir(path.parent)
        self.check()

    def append(self, path, prefix, line):
        self.check()
        before = self.expected[str(path)]
        fd = os.open(path, os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            descriptor = os.fstat(fd)
            if (descriptor.st_dev, descriptor.st_ino) != (before['dev'], before['ino']):
                raise ValueError('ledger descriptor identity differs')
            if os.pread(fd, len(prefix) + 1, 0) != prefix:
                raise ValueError('ledger prefix or tail differs')
            write_all(fd, line); os.fsync(fd)
            linked = self.reader.filesystem_receipt(path)
            if (linked['dev'], linked['ino']) != (before['dev'], before['ino']) or pinned(path, sha(prefix + line)) != prefix + line:
                raise ValueError('ledger append differs')
            for key in ('uid', 'gid', 'mode', 'nlink'):
                if linked[key] != before[key]:
                    raise ValueError('ledger security changed')
            self.expected[str(path)] = linked
        finally:
            os.close(fd)
        self.check()

    def seal_snapshot(self):
        self.check()
        os.chmod(SNAPSHOT, 0o550)
        after = self.reader.filesystem_receipt(SNAPSHOT)
        before = dict(self.expected[str(SNAPSHOT)]); before['mode'] = 0o550
        if {k:v for k,v in before.items() if k != 'ctime_ns'} != {k:v for k,v in after.items() if k != 'ctime_ns'}:
            raise ValueError('snapshot sealing identity differs')
        self.expected[str(SNAPSHOT)] = after
        sync_dir(SNAPSHOT); self.check()


def checkpoint(guard, journal, phase):
    expected_phase = PHASES[len(journal['history'])]
    if phase != expected_phase:
        raise ValueError('recovery phase order differs')
    guard.check()
    journal['phase'] = phase
    journal['history'].append({'phase': phase, 'post_runtime_receipts': {
        str(p): guard.expected[str(p)] for p in (STATE, WORKFLOW, LEDGER, TX)}})
    guard.file(JOURNAL, encode(journal), replace=os.path.lexists(JOURNAL))


def real_toolchain(path):
    process = subprocess.run(['/usr/sbin/runuser', '-u', 'evan-williams', '--',
        str(ROOT / 'env/deeph-v022/bin/python3.9'), '-I', '-S', '-B', str(path), 'verify-toolchain'],
        capture_output=True, text=True, encoding='utf-8', check=False)
    if process.returncode != 0:
        raise ValueError('real UID1000 toolchain failed: ' + process.stderr)
    value = json.loads(process.stdout)
    if value.get('status') != 'PASS' or value.get('build_executed') is not False:
        raise ValueError('toolchain result differs')
    return {'argv': process.args, 'returncode': process.returncode,
            'stdout': process.stdout, 'stderr': process.stderr}


def run(payloads, c, repair, do_write, lock_fd):
    started = time.monotonic()
    require_pristine()
    baseline = json.loads(payloads[BASELINE])
    reader = c.receipts()
    expected = baseline['formal_namespace']
    if len(expected) != 169 or canonical(expected) != '417101edb36bd11ad652e18d5fd4f6b86f36844743d330970cc4a2d051497c7c':
        raise ValueError('169-object parent evidence differs')
    guard = Guard(reader, expected, lock_fd); guard.check()
    raw = baseline_raw(baseline)
    for path, data in raw.items():
        if pinned(path, sha(data)) != data:
            raise ValueError('failure runtime raw bytes differ')
    c.verify_prepared(reader)
    for path in baseline['absent_paths']:
        if os.path.lexists(path):
            raise ValueError('forbidden old product appeared: ' + path)
    require_idle(baseline)
    budget = c.load_bytes('m9_mpi_recovery_budget_readonly', c.OLD_BUDGET,
                         c.read_bytes(c.OLD_BUDGET, c.BASE_SHA, (0, 1000, 0o440)))
    issues = budget.violations(json.loads(raw[STATE]), 1048576)
    if issues != ['ledger_already_hard_stopped']:
        raise ValueError('recovery budget forecast rejected: ' + repr(issues))
    toolchain = real_toolchain(ADAPTER)
    utc = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    bindings = {'record_sha256': sha(payloads[AUTH]), 'frozen_sha256': sha(payloads[FROZEN]),
                'report_sha256': sha(payloads[REPORT]), 'verdict_sha256': sha(payloads[VERDICT])}
    target, event, line = targets(raw, utc, bindings)
    snapshots = {ADAPTER.name: payloads[ADAPTER],
        'm9_openmx_build.original.py': repair.pinned(repair.BASE, repair.BASE_SHA),
        'm9_overlap_common.py': repair.pinned(repair.COMMON, repair.COMMON_SHA),
        'm9_overlap_only_contract.json': repair.pinned(repair.CONTRACT, repair.CONTRACT_SHA)}
    snapshot_manifest = encode({'schema': 'm9-mpi-repair-snapshot-v1', 'members': {
        name: {'bytes': len(data), 'sha256': sha(data)} for name, data in snapshots.items()}})
    journal = {'schema': 'm9-source-build-mpi-recovery-journal-v1', 'recovery_id': RECOVERY_ID,
        'parent_transaction_id': FAILURE_ID, 'utc': utc, 'history': [],
        'baseline_sha256': BASELINE_SHA, 'authorization': bindings,
        'snapshot_sha256': sha(snapshot_manifest), 'derived_driver_sha256': repair.DERIVED_SHA,
        'target_sha256': {str(p): sha(data) for p, data in target.items()},
        'event': event, 'event_line_base64': base64.b64encode(line).decode(),
        'source_build_authorized': False, 'preflight_toolchain': toolchain}
    guard.check(); c.verify_prepared(reader); require_idle(baseline)
    # Re-read every frozen input and closure immediately before the first mutation.
    for path, data in payloads.items():
        pinned(path, sha(data))
    c.verify_sources(json.loads(c.read_bytes(c.FROZEN, 'bc80d1d939527818c7eec747a60cd17c6000f9015374ff33192f34c2f3ae7614')))
    require_pristine()
    if not do_write:
        guard.check()
        return {'status': 'PREFLIGHT_PASS', 'writes': 0, 'build_authorized': False,
                'snapshot_sha256': sha(snapshot_manifest), 'derived_driver_sha256': repair.DERIVED_SHA}
    return commit_recovery(guard, payloads, raw, target, line, snapshots,
                           snapshot_manifest, journal, c, started)


def commit_recovery(guard, payloads, raw, target, line, snapshots,
                    snapshot_manifest, journal, c, started):
    """Mutation seam shared by production and isolated fault-injection tests."""
    guard.directory(PRIVATE, 0)
    for path, data in sorted(payloads.items(), key=lambda item: str(item[0])):
        guard.file(PRIVATE / path.name, data)
    for path, data in raw.items():
        guard.file(PRIVATE / ('before-' + path.name), data)
    checkpoint(guard, journal, 'PREPARED')
    guard.directory(SNAPSHOT, 1000)
    for name, data in snapshots.items():
        guard.file(SNAPSHOT / name, data, gid=1000, mode=0o440)
    guard.file(SNAPSHOT / 'snapshot_manifest.json', snapshot_manifest, gid=1000, mode=0o440)
    guard.seal_snapshot()
    journal['installed_toolchain'] = real_toolchain(SNAPSHOT / ADAPTER.name)
    checkpoint(guard, journal, 'SNAPSHOT_COMMITTED')
    guard.append(LEDGER, raw[LEDGER], line)
    checkpoint(guard, journal, 'LEDGER_COMMITTED')
    for path, phase in ((STATE, 'STATE_COMMITTED'), (WORKFLOW, 'WORKFLOW_COMMITTED')):
        entry = guard.expected[str(path)]
        guard.file(path, target[path], entry['uid'], entry['gid'], entry['mode'], replace=True)
        checkpoint(guard, journal, phase)
    c.verify_prepared(guard.reader)
    guard.check()
    journal['control_elapsed_seconds'] = time.monotonic() - started
    checkpoint(guard, journal, 'SUCCESS_COMMITTED')
    guard.check()
    return {'status': 'RECOVERY_SUCCESS_COMMITTED', 'source_build_authorized': False,
            'snapshot_sha256': sha(snapshot_manifest), 'journal_sha256': sha(pinned(JOURNAL, None)),
            'runtime_sha256': {str(p): sha(pinned(p, None)) for p in (STATE, WORKFLOW, LEDGER, TX)},
            'control_elapsed_seconds': journal['control_elapsed_seconds']}


def main():
    if (os.geteuid() != 0 or sys.version_info[:3] != (3, 9, 23)
            or Path(sys.executable).resolve() != (ROOT / 'env/deeph-v022/bin/python3.9').resolve()
            or not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode)):
        raise SystemExit('root frozen Python3.9.23 -I -S -B required')
    payloads, c, repair = authority(sys.argv[1:])
    fd = os.open(LOCK, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); c.lock_identity(fd)
        result = run(payloads, c, repair, sys.argv[2] == 'recover', fd)
        c.lock_identity(fd)
        print(json.dumps(result, sort_keys=True))
    finally:
        os.close(fd)


if __name__ == '__main__':
    main()
