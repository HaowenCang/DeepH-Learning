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
SNAPSHOT = ROOT / 'controls/source-build-v3'
GATE = ROOT / 'manifests/source_build_v3_gate.json'
PERMIT = ROOT / 'manifests/source_build_v3_execution_permit.json'
PYTHON = ROOT / 'env/deeph-v022/bin/python3.9'
LOCK = ROOT / 'manifests/budget.lock'
LOCK_EXPECTED = (2096, 50700, 1000, 1000, 0o644, 1, 0)
PREPARED = ROOT / 'software/openmx-overlap-build'
RETIRED = ROOT / 'software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired'
OLD_BUDGET = ROOT / 'controls/uid1000-consumer-py39-v2/m9_budget.py'
PROJECT_CONSUMER = PROJECT / '06_reproduction/controllers/m9_source_build_v3_consumer.py'
PROJECT_INSTALLER = PROJECT / '06_reproduction/controllers/m9_source_build_v3_install.py'
FROZEN = PROJECT / '06_reproduction/manifests/m9_source_build_v3_frozen_hashes.json'
AUTHORIZATION = PROJECT / '08_audits/M9_standing_execution_authorization_20260831.md'
WORK = PROJECT / '08_audits/M9_source_build_v3_work_package.md'
TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_v3_consumer.py'
CHAIN_TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_v3_chain.py'
REPORT = PROJECT / '08_audits/M9_source_build_v3_implementation_audit.md'
VERDICT = PROJECT / '08_audits/M9_source_build_v3_implementation_verdict.json'
INSTALL_REPORT = PROJECT / '08_audits/M9_source_build_v3_installation_audit.md'
INSTALL_VERDICT = PROJECT / '08_audits/M9_source_build_v3_installation_verdict.json'
EVIDENCE = PROJECT / '08_audits/M9_source_build_mpi_recovery_v1_postexecution_evidence.json'
FACT = PROJECT / '08_audits/M9_source_build_mpi_recovery_v1_execution_independent_audit.md'
RECEIPTS = PROJECT / '06_reproduction/controllers/m9_py39_consumer_gate_completion.py'
OLD_CONSUMER_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_prepare_py39_uid1000_consumer_frozen_hashes.json'
OLD_OVERLAP_MANIFEST = PROJECT / '06_reproduction/manifests/m9_overlap_py39_recovery_frozen_hashes.json'
OLD_BUILD_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v1_frozen_hashes.json'
OLD_INSTALL_VERDICT = PROJECT / '08_audits/M9_source_build_v1_installation_verdict.json'
CONTRACT = PROJECT / '06_reproduction/configs/m9_overlap_only_contract.json'
OPERATION = '7bc4139f7a9c4b768d3f9ec68c1d1048'
NONCE = 'a930f2b8e7ac449bb251482012eb99d1c7032df764985aaac34519bf6db2013a'
RECOVERY_ID = 'm9-source-build-mpi-recovery-20260831-01'
LAUNCHER = PROJECT / '06_reproduction/controllers/m9_source_build_v3_launcher.py'
REPAIR = PROJECT / '06_reproduction/controllers/m9_openmx_mpi_repair_v1.py'
DECISION = PROJECT / '00_scope/D019_standing_execution_authorization.md'
AUTH_REVIEW = PROJECT / '08_audits/M9_standing_execution_authorization_20260831_independent_review.md'
OLD_V2_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v2_frozen_hashes.json'
REPAIR_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_mpi_recovery_v1_frozen_hashes.json'
DRIVER = PROJECT / '06_reproduction/scripts/m9_openmx_build.py'
DRIVER_BASE_SHA = 'ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec'
DRIVER_DERIVED_SHA = '5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00'
REPAIR_SHA = 'e7b9f13ced60697e62417128c0145d98b9262b614671f4247bcbde19a1f6b027'
SCOPE = 'ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED'
BASE_SHA = 'a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d'
DERIVED_SHA = '94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e'
RECEIPTS_SHA = 'c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55'
EVIDENCE_SHA = '177390748086e678d22c3f24531c5a9b326889e5acb7f3931275262cf27b2ed2'
FACT_SHA = '590121ae5d98c222a2014d315d8f28f08fad95be05cc4c46065e8bf55bd366d2'
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
    'runs/overlap-only-openmx', 'software/openmx-overlap-build.staging',
    'manifests/source_build_v1_execution_permit.json',
    'manifests/source_build_v1_execution_permit.json.tmp')]
SOURCE_PATHS = {PROJECT_CONSUMER, PROJECT_INSTALLER, TEST, WORK, AUTHORIZATION,
                EVIDENCE, FACT, RECEIPTS, OLD_CONSUMER_MANIFEST, OLD_OVERLAP_MANIFEST,
                OLD_BUILD_MANIFEST, OLD_INSTALL_VERDICT, LAUNCHER, REPAIR, DECISION,
                AUTH_REVIEW, OLD_V2_MANIFEST, REPAIR_MANIFEST, CHAIN_TEST}
OLD_MANIFESTS = {
    OLD_CONSUMER_MANIFEST: '765dcf5c09c90ae8d9c2789df1c16f379eca397f18d1dade55167c1b5df207e7',
    OLD_OVERLAP_MANIFEST: '8a3166d61c4f777424f0509ae2d9aae3cc0a6c7f90a725fb9126f5cc25147e3a',
    OLD_BUILD_MANIFEST: 'b3a344e00d3cac19edcf23c69a2631307d6e08714c3a85c85eca8572f2496641',
    OLD_V2_MANIFEST: 'bc80d1d939527818c7eec747a60cd17c6000f9015374ff33192f34c2f3ae7614',
    REPAIR_MANIFEST: '743e3e596d816a7c316a2f7c901b812c650f72bb926aa6698f3c7f72e40818bc',
}
OLD_INSTALL_VERDICT_SHA = '52f5e775d3477688a84da6c409afaf96e6a8f34f44d315f8e17222a2c6ff36a4'
ROOT_ONLY_NAMES = (
    'overlap_source_control_recovery.test-artifact.retired.json',
    'overlap_source_control_recovery_gate.closed-set-invalid.retired.json',
    'overlap_source_control_recovery_gate.json',
    'overlap_source_control_recovery_gate.pre-ledger-fix.retired.json',
    'overlap_source_control_recovery_gate.pre-lock-mode-refresh.retired.json',
    'overlap_source_control_test_artifact_cleanup.json',
    'overlap_source_control_test_artifact_retirement.json',
    'overlap_source_control_test_cleanup_gate.json',
)


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


def root_only_receipts(baseline):
    selected = {}
    fields = {'path', 'dev', 'ino', 'uid', 'gid', 'mode', 'nlink', 'bytes',
              'mtime_ns', 'ctime_ns', 'kind', 'sha256'}
    for name in ROOT_ONLY_NAMES:
        path = str(ROOT / 'manifests' / name)
        value = baseline['formal_namespace'].get(path)
        if (not isinstance(value, dict) or set(value) != fields or value['path'] != path
                or value['kind'] != 'file' or (value['uid'],value['gid'],value['mode'],value['nlink']) != (0,0,0o600,1)
                or not isinstance(value['sha256'], str) or len(value['sha256']) != 64):
            raise SystemExit('fixed root-only receipt malformed or missing: ' + path)
        selected[path] = value
    return selected


def history_attestation(baseline):
    return canonical({'schema':'m9-source-build-history-attestation-v3',
        'baseline_sha256':EVIDENCE_SHA, 'root_only':root_only_receipts(baseline),
        'root_private':{k:v for k,v in baseline['formal_namespace'].items() if k.startswith('/root/')}})


def root_only_metadata(path, attested):
    # Root binds the content hash. UID1000 checks only observable metadata.
    first = os.lstat(path)
    value = {'path':str(path),'dev':first.st_dev,'ino':first.st_ino,'uid':first.st_uid,
             'gid':first.st_gid,'mode':stat.S_IMODE(first.st_mode),'nlink':first.st_nlink,
             'bytes':first.st_size,'mtime_ns':first.st_mtime_ns,'ctime_ns':first.st_ctime_ns,
             'kind':'file','sha256':attested['sha256']}
    second = os.lstat(path)
    keys = ('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')
    if (not stat.S_ISREG(first.st_mode) or any(getattr(first,k)!=getattr(second,k) for k in keys)
            or value != attested):
        raise SystemExit('root-only historical metadata drift: ' + str(path))
    return value


def capture_public_tree(reader, root, attested):
    result = {}
    def visit(path):
        key = str(path)
        receipt = root_only_metadata(path, attested[key]) if key in attested else reader.filesystem_receipt(path)
        result[key] = receipt
        if receipt['kind'] == 'directory':
            names = sorted(p.name for p in path.iterdir())
            for name in names: visit(path / name)
            if sorted(p.name for p in path.iterdir()) != names or reader.filesystem_receipt(path) != receipt:
                raise SystemExit('public historical directory drift: ' + key)
    visit(root)
    return result


def runtime_and_history(reader, baseline, installed=False, private=False):
    """Compare the independently audited recovery baseline; additions are closed."""
    roots = [ROOT / 'manifests', ROOT / 'controls']
    if private:
        roots.append(Path('/root/deeph-m9-control'))
    current = {}
    attested = root_only_receipts(baseline)
    for path in roots:
        # Root/private checks always hash actual bytes, including all eight.
        current.update(reader.capture_tree(path) if private else capture_public_tree(reader, path, attested))
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
    if set(frozen) != {'schema', 'files'} or frozen['schema'] != 'm9-source-build-frozen-v3':
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
    read_bytes(OLD_INSTALL_VERDICT, OLD_INSTALL_VERDICT_SHA)


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
    if set(manifest) != {'schema', 'members'} or manifest['schema'] != 'm9-source-build-snapshot-v3':
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
    verify_verdict(json.loads(payloads[VERDICT.name]), 'm9-source-build-implementation-verdict-v3',
                   gate['frozen_sha256'], REPORT, gate['report_sha256'])
    return payloads


def validate_gate(gate):
    if (set(gate) != {'schema', 'status', 'scope', 'action', 'operation_id', 'nonce',
                     'frozen_sha256', 'snapshot_sha256', 'report_sha256', 'verdict_sha256',
                     'authorization_sha256', 'history_attestation_sha256', 'runtime'}
            or gate['schema'] != 'm9-source-build-readiness-v3'
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
    if gate['history_attestation_sha256'] != history_attestation(baseline):
        raise SystemExit('root history attestation binding differs')
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
            or state.get('recovered_from_source_build_mpi_failure') != RECOVERY_ID
            or workflow.get('recovered_from_source_build_mpi_failure') != RECOVERY_ID
            or tx['state'] != 'FAILED_COMMITTED' or tx['action'] != 'source_build'
            or tx['transaction_id'] != '38a891fff6fd07675581b891766e02c6'):
        raise SystemExit('build preexecution terminal state mismatch')
    verify_prepared(reader)
    if require_permit:
        permit = json.loads(read_bytes(PERMIT, owner=(0, 1000, 0o640)))
        if (set(permit) != {'schema', 'gate_sha256', 'operation_id', 'nonce',
                           'report_sha256', 'verdict_sha256'}
                or permit['schema'] != 'm9-source-build-execution-permit-v3'
                or permit['gate_sha256'] != sha(raw)
                or permit['operation_id'] != OPERATION or permit['nonce'] != NONCE):
            raise SystemExit('build execution permit binding differs')
        report = read_bytes(INSTALL_REPORT, permit['report_sha256'])
        verdict = json.loads(read_bytes(INSTALL_VERDICT, permit['verdict_sha256']))
        verify_verdict(verdict, 'm9-source-build-installation-verdict-v3',
                       gate['frozen_sha256'], INSTALL_REPORT, sha(report))
    terminal = runtime_and_history(reader, baseline, installed=True)
    if terminal != runtime:
        raise SystemExit('build runtime drift during verification')
    return gate


def execution_binding():
    """Static installed authority, valid also while the budget owns a running tx.

    This is NOT a readiness check and must never replace verify_gate at first write.
    """
    gate_raw = read_bytes(GATE, owner=(0, 1000, 0o640))
    gate = json.loads(gate_raw); validate_gate(gate)
    payloads = read_snapshot(gate)
    if sha(payloads[AUTHORIZATION.name]) != gate['authorization_sha256']:
        raise SystemExit('static execution user authority mismatch')
    permit_raw = read_bytes(PERMIT, owner=(0, 1000, 0o640))
    permit = json.loads(permit_raw)
    if (set(permit) != {'schema', 'gate_sha256', 'operation_id', 'nonce',
                       'report_sha256', 'verdict_sha256'}
            or permit['schema'] != 'm9-source-build-execution-permit-v3'
            or permit['gate_sha256'] != sha(gate_raw)
            or permit['operation_id'] != OPERATION or permit['nonce'] != NONCE):
        raise SystemExit('static execution permit mismatch')
    fact = read_bytes(INSTALL_REPORT, permit['report_sha256'])
    verdict = json.loads(read_bytes(INSTALL_VERDICT, permit['verdict_sha256']))
    verify_verdict(verdict, 'm9-source-build-installation-verdict-v3',
                   gate['frozen_sha256'], INSTALL_REPORT, sha(fact))
    return {'operation_id': OPERATION, 'gate_sha256': sha(gate_raw),
            'permit_sha256': sha(permit_raw), 'snapshot_sha256': gate['snapshot_sha256'],
            'consumer_sha256': sha(payloads[PROJECT_CONSUMER.name]),
            'launcher_sha256': sha(payloads[LAUNCHER.name]),
            'driver_base_sha256': DRIVER_BASE_SHA, 'driver_derived_sha256': DRIVER_DERIVED_SHA}


def validate_launcher_receipt(capability_id, transaction_id, budget_bootstrap):
    # The immutable budget catches Exception here to commit CPU and HARD_STOP.
    # A static authority failure is a failed receipt, not a process exit request.
    try:
        return _validate_launcher_receipt(capability_id, transaction_id, budget_bootstrap)
    except SystemExit as exc:
        raise ValueError('v3 post-child authority validation failed: ' + str(exc)) from exc


def _validate_launcher_receipt(capability_id, transaction_id, budget_bootstrap):
    binding = execution_binding()
    directory = ROOT / 'manifests/overlap_capabilities'
    receipt_raw = read_bytes(directory / (capability_id + '.launcher-receipt.json'),
                             owner=(1000, 1000, 0o600))
    consumed_raw = read_bytes(directory / (capability_id + '.consumed.json'),
                              owner=(1000, 1000, 0o600))
    receipt, consumed = json.loads(receipt_raw), json.loads(consumed_raw)
    parent_argv = [str(PYTHON.resolve()), '-I', '-S', '-B',
                   str(SNAPSHOT / PROJECT_CONSUMER.name), *RUN_ARGV]
    child_argv = [str(PYTHON.resolve()), '-I', '-S', '-B',
                  str(SNAPSHOT / LAUNCHER.name), '--capability-id', capability_id]
    if (receipt.get('schema_version') != 'm9-overlap-source-launcher-receipt-v1'
            or receipt.get('status') != 'PASS' or receipt.get('capability_id') != capability_id
            or receipt.get('transaction_id') != transaction_id
            or receipt.get('budget_bootstrap') != budget_bootstrap
            or receipt.get('v3_binding') != binding
            or consumed.get('schema_version') != 'm9-overlap-capability-v1'
            or consumed.get('state') != 'CONSUMED' or consumed.get('capability_id') != capability_id
            or consumed.get('transaction_id') != transaction_id
            or consumed.get('action') != 'source_build' or consumed.get('structure_id') is not None
            or consumed.get('bucket') != 'overlap_build'
            or consumed.get('forecast_bytes') != 4294967296
            or consumed.get('budget_bootstrap') != budget_bootstrap
            or consumed.get('budget_argv') != parent_argv or consumed.get('launcher_argv') != child_argv):
        raise ValueError('v3 launcher receipt/capability/authority mismatch')
    bootstrap = receipt.get('launcher_bootstrap')
    if (not isinstance(bootstrap, dict) or bootstrap.get('isolated') is not True
            or bootstrap.get('no_site') is not True or bootstrap.get('dont_write_bytecode') is not True
            or set(bootstrap.get('modules', {})) != {'argparse', 'hashlib', 'json', 'pathlib'}
            or bootstrap.get('python_executable') != str(PYTHON.resolve())):
        raise ValueError('v3 launcher bootstrap provenance mismatch')
    dependency = receipt.get('dependency_path')
    if (not isinstance(dependency, dict)
            or dependency.get('path') != str(PYTHON.parent.parent / 'lib/python3.9/site-packages')
            or dependency.get('added_after_capability') is not True
            or dependency.get('method') != 'sys.path.append'
            or dependency.get('site_addsitedir_called') is not False
            or dependency.get('pth_processed') is not False):
        raise ValueError('v3 source dependency provenance mismatch')
    sources = receipt.get('loaded_sources')
    if not isinstance(sources, dict) or set(sources) != {'m9_overlap_common', 'm9_openmx_build'}:
        raise ValueError('v3 loaded module closure mismatch')
    frozen = json.loads(read_bytes(OLD_OVERLAP_MANIFEST, OLD_MANIFESTS[OLD_OVERLAP_MANIFEST]))['files']
    for name, value in sources.items():
        if not isinstance(value, dict):
            raise ValueError('v3 invalid loaded source receipt')
        path = str(DRIVER.parent / (name + '.py'))
        fields = {'path', 'sha256', 'loader', 'origin', 'bytecode_consulted'}
        expected = frozen[path]
        if name == 'm9_openmx_build':
            fields.add('base_sha256'); expected = DRIVER_DERIVED_SHA
            if value.get('base_sha256') != DRIVER_BASE_SHA or frozen[path] != DRIVER_BASE_SHA:
                raise ValueError('v3 driver derivation provenance mismatch')
        if (not isinstance(value, dict) or set(value) != fields or value.get('path') != path
                or value.get('sha256') != expected or value.get('loader') != 'FrozenSourceLoader'
                or value.get('origin') != path or value.get('bytecode_consulted') is not False):
            raise ValueError('v3 actual loaded source mismatch: ' + name)
    return sha(receipt_raw)


def lock_identity(fd):
    a, b = os.fstat(fd), os.lstat(LOCK)
    expected = LOCK_EXPECTED
    for item in (a, b):
        if (item.st_dev, item.st_ino, item.st_uid, item.st_gid,
                stat.S_IMODE(item.st_mode), item.st_nlink, item.st_size) != expected:
            raise SystemExit('original build budget lock identity differs')


def fixed_runtime():
    if (sys.version_info[:3] != (3, 9, 23) or Path(sys.executable).resolve() != PYTHON.resolve()
            or not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode):
        raise SystemExit('requires frozen Python 3.9.23 -I -S -B')


def guard_budget(m9):
    m9.OVERLAP_SOURCE_LAUNCHER = SNAPSHOT / LAUNCHER.name
    m9.validate_launcher_receipt = validate_launcher_receipt
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
