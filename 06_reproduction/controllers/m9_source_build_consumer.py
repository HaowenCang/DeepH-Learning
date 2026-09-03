"""Versioned, one-action consumer for the approved M9 source build.

Old controls stay byte-identical. The budget implementation is an exact
two-literal derivation; all accounting, transactions and child code are reused.
"""
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
ROOT = Path('/home/evan-williams/deeph-m9')
SNAPSHOT = ROOT / 'controls/source-build-v1'
GATE = ROOT / 'manifests/source_build_v1_gate.json'
PERMIT = ROOT / 'manifests/source_build_v1_execution_permit.json'
PYTHON = ROOT / 'env/deeph-v022/bin/python3.9'
LOCK = ROOT / 'manifests/budget.lock'
PREPARED = ROOT / 'software/openmx-overlap-build'
RETIRED = ROOT / 'software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired'
OLD_BUDGET = ROOT / 'controls/uid1000-consumer-py39-v2/m9_budget.py'
PROJECT_CONSUMER = PROJECT / '06_reproduction/controllers/m9_source_build_consumer.py'
PROJECT_INSTALLER = PROJECT / '06_reproduction/controllers/m9_source_build_install.py'
FROZEN = PROJECT / '06_reproduction/manifests/m9_source_build_v1_frozen_hashes.json'
AUTHORIZATION = PROJECT / '08_audits/M9_source_build_v1_user_authorization.md'
WORK = PROJECT / '08_audits/M9_source_build_v1_work_package.md'
TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_consumer.py'
REPORT = PROJECT / '08_audits/M9_source_build_v1_implementation_audit.md'
VERDICT = PROJECT / '08_audits/M9_source_build_v1_implementation_verdict.json'
INSTALL_REPORT = PROJECT / '08_audits/M9_source_build_v1_installation_audit.md'
INSTALL_VERDICT = PROJECT / '08_audits/M9_source_build_v1_installation_verdict.json'
EVIDENCE = PROJECT / '08_audits/M9_source_prepare_py39_fresh_postexecution_evidence.json'
FACT = PROJECT / '08_audits/M9_source_prepare_py39_fresh_execution_independent_audit.md'
RECEIPTS = PROJECT / '06_reproduction/controllers/m9_py39_consumer_gate_completion.py'
OLD_CONSUMER_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_prepare_py39_uid1000_consumer_frozen_hashes.json'
OLD_OVERLAP_MANIFEST = PROJECT / '06_reproduction/manifests/m9_overlap_py39_recovery_frozen_hashes.json'
CONTRACT = PROJECT / '06_reproduction/configs/m9_overlap_only_contract.json'
OPERATION = '72cefbe283654fd5b85fb2e66d9c2dfb'
NONCE = '3bd3367fc192e9485bfa3c68679ab6636fb6af6d86e5f48bf848e96494c84f83'
SCOPE = 'ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED'
BASE_SHA = 'a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d'
DERIVED_SHA = '94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e'
RECEIPTS_SHA = 'c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55'
EVIDENCE_SHA = 'ee4d593ddb277a252cbd3a90b0e59f94b96fc1d614e2544dde22bb5b217f8455'
FACT_SHA = '89418b784d800e25d895b05360ecd086be217e5a820dcdca526ef0205b1cde71'
PREPARED_SHA = '7510fa41cfe9396e5cb2ae94728f4825b3b1ba3a1496bdd86debaf55c4229260'
RETIRED_SHA = '060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359'
OLD_BLOCK = b'                != "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018"\n                or action != "source_prepare"'
NEW_BLOCK = b'                != "ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED"\n                or action != "source_build"'
RUN_ARGV = ['run', '--build-operation-id', OPERATION, '--bucket', 'none',
            '--cpu-bucket', 'overlap_build', '--forecast-bytes', '4294967296',
            '--overlap-operation', '--overlap-action', 'source_build', '--config', str(CONTRACT)]
MUTABLE_RUNTIME = {str(ROOT / 'manifests' / n) for n in (
    'budget_state.json', 'overlap_workflow_state.json', 'overlap_transaction.json',
    'budget_ledger.jsonl', 'openmx_official_3.9.9_tree_manifest.json')}
FORBIDDEN_PRODUCTS = [ROOT / p for p in (
    'env/hdf5-1.12.1', 'manifests/openmx_overlap_tree_manifest.json',
    'manifests/openmx_overlap_build_manifest.json', 'logs/overlap-build',
    'runs/overlap-only-openmx', 'software/openmx-overlap-build.staging')]
SOURCE_PATHS = {PROJECT_CONSUMER, PROJECT_INSTALLER, TEST, WORK, AUTHORIZATION,
                EVIDENCE, FACT, RECEIPTS, OLD_CONSUMER_MANIFEST, OLD_OVERLAP_MANIFEST}
OLD_MANIFESTS = {
    OLD_CONSUMER_MANIFEST: '765dcf5c09c90ae8d9c2789df1c16f379eca397f18d1dade55167c1b5df207e7',
    OLD_OVERLAP_MANIFEST: '8a3166d61c4f777424f0509ae2d9aae3cc0a6c7f90a725fb9126f5cc25147e3a',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode('utf-8'))


def read_bytes(path, expected=None, owner=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        with os.fdopen(os.dup(fd), 'rb') as stream:
            payload = stream.read()
        after, linked = os.fstat(fd), os.lstat(path)
        fields = ('st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_mode', 'st_nlink',
                  'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or any(getattr(before, k) != getattr(after, k)
                       or getattr(after, k) != getattr(linked, k) for k in fields)
                or len(payload) != after.st_size
                or expected is not None and sha(payload) != expected
                or owner is not None and (before.st_uid, before.st_gid,
                    stat.S_IMODE(before.st_mode)) != owner):
            raise SystemExit('build control receipt mismatch: ' + str(path))
        return payload
    finally:
        os.close(fd)


def load_bytes(name, path, payload):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(payload, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def derive_budget(payload):
    if sha(payload) != BASE_SHA or payload.count(OLD_BLOCK) != 1:
        raise SystemExit('budget derivation base or exact match differs')
    result = payload.replace(OLD_BLOCK, NEW_BLOCK, 1)
    if sha(result) != DERIVED_SHA:
        raise SystemExit('budget derivation hash differs')
    return result


def receipts(installed=False):
    path = SNAPSHOT / RECEIPTS.name if installed else RECEIPTS
    return load_bytes('m9_build_receipts', path,
        read_bytes(path, RECEIPTS_SHA, (0, 1000, 0o440) if installed else None))


def runtime_and_history(reader, baseline, installed=False, private=False):
    """Compare the immutable source_prepare baseline; additions are closed."""
    roots = [ROOT / 'manifests', ROOT / 'controls']
    if private:
        roots.append(Path('/root/deeph-m9-control'))
    current = {}
    for path in roots:
        current.update(reader.capture_tree(path))
    expected = {k: v for k, v in baseline['formal_namespace'].items()
                if private or not k.startswith('/root/')}
    extras = set()
    if installed:
        extras = {str(p) for p in [SNAPSHOT, *SNAPSHOT.iterdir()]}
        if os.path.lexists(GATE):
            extras.add(str(GATE))
        if os.path.lexists(PERMIT):
            extras.add(str(PERMIT))
    if set(current) != set(expected) | extras:
        raise SystemExit('build historical namespace closure mismatch')
    for path, value in expected.items():
        observed = dict(current[path])
        wanted = dict(value)
        if installed and path in (str(ROOT / 'controls'), str(ROOT / 'manifests')):
            for field in ('mtime_ns', 'ctime_ns', 'bytes'):
                observed.pop(field); wanted.pop(field)
            if path == str(ROOT / 'controls'):
                wanted['nlink'] += 1
        if observed != wanted:
            raise SystemExit('build historical/runtime drift: ' + path)
    return {k: current[k] for k in sorted(MUTABLE_RUNTIME)}


def verify_prepared(reader):
    for path in FORBIDDEN_PRODUCTS:
        if os.path.lexists(path):
            raise SystemExit('preexisting build product: ' + str(path))
    prepared = reader.capture_tree(PREPARED)
    if canonical(prepared) != PREPARED_SHA:
        raise SystemExit('complete prepared source tree drift')
    if canonical(reader.capture_tree(RETIRED)) != RETIRED_SHA:
        raise SystemExit('retired failure tree drift')
    # Hashes cover every file, directory, inode, permission and timestamp;
    # exact namespaces also reject additions, links and special objects.


def verify_sources(frozen):
    if set(frozen) != {'schema', 'files'} or frozen['schema'] != 'm9-source-build-frozen-v1':
        raise SystemExit('build frozen manifest schema mismatch')
    if set(frozen['files']) != {str(p) for p in SOURCE_PATHS}:
        raise SystemExit('build source closure mismatch')
    for path, digest in frozen['files'].items():
        read_bytes(Path(path), digest)
    for path, digest in OLD_MANIFESTS.items():
        nested = json.loads(read_bytes(path, digest))
        for member, member_sha in nested['files'].items():
            read_bytes(Path(member), member_sha)
    read_bytes(EVIDENCE, EVIDENCE_SHA)
    read_bytes(FACT, FACT_SHA)


def verify_verdict(value, schema, frozen_sha, report_path, report_sha):
    if (set(value) != {'schema', 'status', 'blocking', 'non_blocking',
                      'frozen_sha256', 'report_path', 'report_sha256'}
            or value['schema'] != schema or value['status'] != 'PASS'
            or type(value['blocking']) is not int or value['blocking'] != 0
            or type(value['non_blocking']) is not int or value['non_blocking'] != 0
            or value['frozen_sha256'] != frozen_sha
            or value['report_path'] != str(report_path)
            or value['report_sha256'] != report_sha):
        raise SystemExit('build independent verdict mismatch')


def read_snapshot(gate):
    observed = os.lstat(SNAPSHOT)
    if (not stat.S_ISDIR(observed.st_mode)
            or (observed.st_uid, observed.st_gid, stat.S_IMODE(observed.st_mode)) != (0, 1000, 0o550)):
        raise SystemExit('build snapshot root metadata mismatch')
    raw = read_bytes(SNAPSHOT / 'snapshot_manifest.json', gate['snapshot_sha256'], (0, 1000, 0o440))
    manifest = json.loads(raw)
    names = {p.name for p in SOURCE_PATHS | {FROZEN, REPORT, VERDICT}} | {'m9_budget_source_build.py'}
    if set(manifest) != {'schema', 'members'} or manifest['schema'] != 'm9-source-build-snapshot-v1':
        raise SystemExit('build snapshot schema mismatch')
    if set(manifest['members']) != names or {p.name for p in SNAPSHOT.iterdir()} != names | {'snapshot_manifest.json'}:
        raise SystemExit('build snapshot actual closure mismatch')
    payloads = {}
    for name, entry in manifest['members'].items():
        if set(entry) != {'bytes', 'sha256'}:
            raise SystemExit('snapshot entry fields differ')
        payload = read_bytes(SNAPSHOT / name, entry['sha256'], (0, 1000, 0o440))
        if len(payload) != entry['bytes']:
            raise SystemExit('snapshot member size differs')
        payloads[name] = payload
    frozen_raw = payloads[FROZEN.name]
    if sha(frozen_raw) != gate['frozen_sha256']:
        raise SystemExit('snapshot frozen binding differs')
    frozen = json.loads(frozen_raw)
    verify_sources(frozen)
    for path, expected in frozen['files'].items():
        if sha(payloads[Path(path).name]) != expected:
            raise SystemExit('snapshot source binding differs')
    if sha(payloads['m9_budget_source_build.py']) != DERIVED_SHA:
        raise SystemExit('snapshot budget derivation differs')
    if sha(payloads[REPORT.name]) != gate['report_sha256'] or sha(payloads[VERDICT.name]) != gate['verdict_sha256']:
        raise SystemExit('snapshot implementation audit differs')
    verify_verdict(json.loads(payloads[VERDICT.name]), 'm9-source-build-implementation-verdict-v1',
                   gate['frozen_sha256'], REPORT, gate['report_sha256'])
    return payloads


def validate_gate(gate):
    if (set(gate) != {'schema', 'status', 'scope', 'action', 'operation_id', 'nonce',
                     'frozen_sha256', 'snapshot_sha256', 'report_sha256', 'verdict_sha256',
                     'authorization_sha256', 'runtime'}
            or gate['schema'] != 'm9-source-build-readiness-v1'
            or gate['status'] != 'PASS' or gate['scope'] != SCOPE
            or gate['action'] != 'source_build' or gate['operation_id'] != OPERATION
            or gate['nonce'] != NONCE):
        raise SystemExit('build gate scope/field mismatch')


def require_argv(argv):
    if argv != RUN_ARGV:
        raise SystemExit('build consumer requires the unique approved argv')
    return [argv[0], *argv[3:]]


def verify_gate(require_permit=True):
    raw = read_bytes(GATE, owner=(0, 1000, 0o640))
    gate = json.loads(raw); validate_gate(gate)
    payloads = read_snapshot(gate)
    if sha(payloads[AUTHORIZATION.name]) != gate['authorization_sha256']:
        raise SystemExit('build user authorization binding differs')
    reader = receipts(installed=True)
    baseline = json.loads(payloads[EVIDENCE.name])
    runtime = runtime_and_history(reader, baseline, installed=True)
    if gate['runtime'] != runtime:
        raise SystemExit('build runtime differs from readiness gate')
    state = json.loads(read_bytes(ROOT / 'manifests/budget_state.json'))
    workflow = json.loads(read_bytes(ROOT / 'manifests/overlap_workflow_state.json'))
    tx = json.loads(read_bytes(ROOT / 'manifests/overlap_transaction.json'))
    if (state['hard_stopped'] or workflow['hard_stopped']
            or state['active_overlap_transaction'] is not None or workflow['active_transaction'] is not None
            or state['wall_clock_policy']['mode'] != 'UNLIMITED'
            or workflow['stage'] != 'SOURCES_PREPARED'
            or tx['state'] != 'SUCCESS_COMMITTED' or tx['action'] != 'source_prepare'
            or tx['transaction_id'] != 'dc75dda112af553377a697f629801782'):
        raise SystemExit('build preexecution terminal state mismatch')
    verify_prepared(reader)
    if require_permit:
        permit = json.loads(read_bytes(PERMIT, owner=(0, 1000, 0o640)))
        if (set(permit) != {'schema', 'gate_sha256', 'operation_id', 'nonce',
                           'report_sha256', 'verdict_sha256'}
                or permit['schema'] != 'm9-source-build-execution-permit-v1'
                or permit['gate_sha256'] != sha(raw)
                or permit['operation_id'] != OPERATION or permit['nonce'] != NONCE):
            raise SystemExit('build execution permit binding differs')
        report = read_bytes(INSTALL_REPORT, permit['report_sha256'])
        verdict = json.loads(read_bytes(INSTALL_VERDICT, permit['verdict_sha256']))
        verify_verdict(verdict, 'm9-source-build-installation-verdict-v1',
                       gate['frozen_sha256'], INSTALL_REPORT, sha(report))
    terminal = runtime_and_history(reader, baseline, installed=True)
    if terminal != runtime:
        raise SystemExit('build runtime drift during verification')
    return gate


def lock_identity(fd):
    a, b = os.fstat(fd), os.lstat(LOCK)
    expected = (2096, 50700, 1000, 1000, 0o644, 1, 0)
    for item in (a, b):
        if (item.st_dev, item.st_ino, item.st_uid, item.st_gid,
                stat.S_IMODE(item.st_mode), item.st_nlink, item.st_size) != expected:
            raise SystemExit('original build budget lock identity differs')


def fixed_runtime():
    if (sys.version_info[:3] != (3, 9, 23) or Path(sys.executable).resolve() != PYTHON.resolve()
            or not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode):
        raise SystemExit('requires frozen Python 3.9.23 -I -S -B')


def guard_budget(m9):
    atomic = m9.atomic_json
    first_write = True
    def ready():
        # The original controller calls these proxies while holding budget.lock.
        return verify_gate(True)
    def guarded_atomic(path, value):
        nonlocal first_write
        if first_write:
            ready(); first_write = False
        atomic(path, value)
    m9.verify_unlimited_wall_clock_execution_ready = ready
    m9.verify_unlimited_wall_clock_execution_fact_gate = lambda: {'gate': ready()}
    m9.d018_execution_runtime_receipts = lambda: ready()['runtime']
    m9.atomic_json = guarded_atomic
    return m9


def main():
    if Path(__file__) != SNAPSHOT / PROJECT_CONSUMER.name or os.geteuid() != 1000:
        raise SystemExit('build consumer requires installed source and real UID1000')
    fixed_runtime()
    argv = list(sys.argv[1:])
    verify_only = argv in (['verify-ready'], ['verify-execution'])
    delegated = None if verify_only else require_argv(argv)
    fd = os.open(LOCK, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX); lock_identity(fd)
        gate = verify_gate(require_permit=argv != ['verify-ready'])
        lock_identity(fd)
    finally:
        os.close(fd)
    if verify_only:
        print(json.dumps({'status': 'PASS', 'action': 'source_build',
                          'source_build_executed': False, 'runtime_sha256': canonical(gate['runtime'])}))
        return 0
    budget_path = SNAPSHOT / 'm9_budget_source_build.py'
    m9 = guard_budget(load_bytes('m9_source_build_budget', budget_path,
                    read_bytes(budget_path, DERIVED_SHA, (0, 1000, 0o440))))
    sys.argv = [str(SNAPSHOT / PROJECT_CONSUMER.name), *delegated]
    return int(m9.main())


if __name__ == '__main__':
    raise SystemExit(main())
