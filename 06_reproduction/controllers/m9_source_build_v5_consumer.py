"""Versioned, one-action consumer for the approved M9 source build.

Old controls stay byte-identical. The budget implementation is an exact
two-literal derivation; all accounting, transactions and child code are reused.
"""
import base64
import fcntl
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
ROOT = Path('/home/evan-williams/deeph-m9')
SNAPSHOT = ROOT / 'controls/source-build-v5'
GATE = ROOT / 'manifests/source_build_v5_gate.json'
PERMIT = ROOT / 'manifests/source_build_v5_execution_permit.json'
PYTHON = ROOT / 'env/deeph-v022/bin/python3.9'
LOCK = ROOT / 'manifests/budget.lock'
LOCK_EXPECTED = (2096, 50700, 1000, 1000, 0o644, 1, 0)
PREPARED = ROOT / 'software/openmx-overlap-build'
RETIRED = ROOT / 'software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired'
OLD_BUDGET = ROOT / 'controls/uid1000-consumer-py39-v2/m9_budget.py'
PROJECT_CONSUMER = PROJECT / '06_reproduction/controllers/m9_source_build_v5_consumer.py'
PROJECT_INSTALLER = PROJECT / '06_reproduction/controllers/m9_source_build_v5_install.py'
FROZEN = PROJECT / '06_reproduction/manifests/m9_source_build_v5_frozen_hashes.json'
AUTHORIZATION = PROJECT / '08_audits/M9_standing_execution_authorization_20260831.md'
WORK = PROJECT / '08_audits/M9_source_build_v5_work_package.md'
TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_v5_consumer.py'
CHAIN_TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_v5_chain.py'
REPORT = PROJECT / '08_audits/M9_source_build_v5_implementation_audit.md'
VERDICT = PROJECT / '08_audits/M9_source_build_v5_implementation_verdict.json'
INSTALL_REPORT = PROJECT / '08_audits/M9_source_build_v5_installation_audit.md'
INSTALL_VERDICT = PROJECT / '08_audits/M9_source_build_v5_installation_verdict.json'
EVIDENCE = PROJECT / '08_audits/M9_source_build_v5_parent_namespace_evidence.json'
RECOVERY_EVIDENCE = PROJECT / '08_audits/M9_source_build_wsl_shutdown_recovery_v2_postexecution_evidence.json'
FACT = PROJECT / '08_audits/M9_source_build_wsl_shutdown_recovery_v2_execution_independent_audit.md'
RECEIPTS = PROJECT / '06_reproduction/controllers/m9_py39_consumer_gate_completion.py'
OLD_CONSUMER_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_prepare_py39_uid1000_consumer_frozen_hashes.json'
OLD_OVERLAP_MANIFEST = PROJECT / '06_reproduction/manifests/m9_overlap_py39_recovery_frozen_hashes.json'
OLD_BUILD_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v1_frozen_hashes.json'
OLD_INSTALL_VERDICT = PROJECT / '08_audits/M9_source_build_v1_installation_verdict.json'
CONTRACT = PROJECT / '06_reproduction/configs/m9_overlap_only_contract.json'
OPERATION = 'c35a556951014126894fda5a99e5c101'
NONCE = '4bf38debe62983e08de29305b48483066a876c190de0c2b170d9ed61fb141cc0'
RECOVERY_ID = 'm9-source-build-wsl-shutdown-recovery-20260902-01'
LAUNCHER = PROJECT / '06_reproduction/controllers/m9_source_build_v5_launcher.py'
REPAIR = PROJECT / '06_reproduction/controllers/m9_openmx_mpi_repair_v1.py'
DECISION = PROJECT / '00_scope/D019_standing_execution_authorization.md'
AUTH_REVIEW = PROJECT / '08_audits/M9_standing_execution_authorization_20260831_independent_review.md'
OLD_V2_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v2_frozen_hashes.json'
REPAIR_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_mpi_recovery_v1_frozen_hashes.json'
OLD_V3_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v3_frozen_hashes.json'
HOST_RECOVERY_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_host_shutdown_recovery_v1_frozen_hashes.json'
OLD_V3_INSTALL_VERDICT = PROJECT / '08_audits/M9_source_build_v3_installation_verdict.json'
OLD_V4_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v4_frozen_hashes.json'
WSL_RECOVERY_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_wsl_shutdown_recovery_v2_frozen_hashes.json'
OLD_V4_INSTALL_VERDICT = PROJECT / '08_audits/M9_source_build_v4_installation_verdict.json'
DRIVER = PROJECT / '06_reproduction/scripts/m9_openmx_build.py'
DRIVER_BASE_SHA = 'ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec'
DRIVER_DERIVED_SHA = '5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00'
REPAIR_SHA = 'e7b9f13ced60697e62417128c0145d98b9262b614671f4247bcbde19a1f6b027'
SCOPE = 'ALLOW_ONE_SOURCE_BUILD_AFTER_PREPARED'
BASE_SHA = 'a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d'
DERIVED_SHA = '94050d73f498b84ab0054f64f1b04ea8667067f86a54ed3f352e6b926a9e691e'
RECEIPTS_SHA = 'c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55'
EVIDENCE_SHA = '8a02bc5650cf75e9e86f200204e9fe449c516c5693ff98b526ae8d45243506be'
RECOVERY_EVIDENCE_SHA = 'b3477ede6590cda56d5cf45bb1a16809e591d6aa5858531807f5cc1513eaca36'
FACT_SHA = '4d1d8b20327256b807203861f69e850d104858bc86a13e77dde77dff8f2c9e4b'
PARENT_FORMAL_SHA = '5153de04dd6a33f8851cd898d8af9c8e655a57a161d31f70a7f60dc8032c0f42'
PREPARED_SHA = 'c9ac7a5cb34ef582ce06965d568a6fe0ded9ef4f2a51e2c07ab1e5e1898f1521'
RETIRED_SHA = '060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359'
PARENT_RUNTIME_SHA = {
    'budget_state.json': 'c45337d97584abbce0c885ca233d9fd9bd9b548d17847a52a7f1b398fc9c1dec',
    'overlap_workflow_state.json': '96778c2501f2d7eca33b973266e4a8e33e22bc65238cd0b9f12d014a3c5c7aa7',
    'overlap_transaction.json': 'cf17e84abf1303438220ad3a872375e779de19052a10cf2cee41055f0d04ed91',
    'budget_ledger.jsonl': '24253c63284171f826b6b068053e8bd7fe1fd1a8e2feadbca3f5885f4443ed8b',
}
PRESERVED_V4_AUTHORITY = {
    'consumed_capability_sha256': '8d6aff34eec0ee29ce8a7b8e6a8fdf8a76b78ec1fe5a5bd584ee1e2587607204',
    'gate_sha256': 'dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1',
    'permit_sha256': 'c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4',
    'launcher_receipt_present': False,
}
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
                EVIDENCE, RECOVERY_EVIDENCE, FACT, RECEIPTS, OLD_CONSUMER_MANIFEST, OLD_OVERLAP_MANIFEST,
                OLD_BUILD_MANIFEST, OLD_INSTALL_VERDICT, LAUNCHER, REPAIR, DECISION,
                AUTH_REVIEW, OLD_V2_MANIFEST, REPAIR_MANIFEST, OLD_V3_MANIFEST,
                HOST_RECOVERY_MANIFEST, OLD_V3_INSTALL_VERDICT, OLD_V4_MANIFEST,
                WSL_RECOVERY_MANIFEST, OLD_V4_INSTALL_VERDICT, CHAIN_TEST}
OLD_MANIFESTS = {
    OLD_CONSUMER_MANIFEST: '765dcf5c09c90ae8d9c2789df1c16f379eca397f18d1dade55167c1b5df207e7',
    OLD_OVERLAP_MANIFEST: '8a3166d61c4f777424f0509ae2d9aae3cc0a6c7f90a725fb9126f5cc25147e3a',
    OLD_BUILD_MANIFEST: 'b3a344e00d3cac19edcf23c69a2631307d6e08714c3a85c85eca8572f2496641',
    OLD_V2_MANIFEST: 'bc80d1d939527818c7eec747a60cd17c6000f9015374ff33192f34c2f3ae7614',
    REPAIR_MANIFEST: '743e3e596d816a7c316a2f7c901b812c650f72bb926aa6698f3c7f72e40818bc',
    OLD_V3_MANIFEST: '01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58',
    HOST_RECOVERY_MANIFEST: '3334010925f97486f58b2b3116b52b6b4cc48f34d4c8e0e1ec801de577bbc668',
    OLD_V4_MANIFEST: '5862155306e595f268e996a9712194faabd2347e94b73a0118ebb403c763cf09',
    WSL_RECOVERY_MANIFEST: '139fb44a695873f1771fa05bd15bc28a9ac348ee2f6fc8a567080c7e920b1e62',
}
OLD_INSTALL_VERDICT_SHA = '52f5e775d3477688a84da6c409afaf96e6a8f34f44d315f8e17222a2c6ff36a4'
OLD_V3_INSTALL_VERDICT_SHA = '60b22f6a0a8ba2f756d4829aa461f6d0ffdcf79d681c4d15c22a5c3671abc755'
OLD_V4_INSTALL_VERDICT_SHA = 'fae99d0d4cda77565f1bbccfe9d04630ff60be3b7026d4c82649a72880dc4b56'
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


def baseline_namespace(baseline):
    formal = baseline.get('formal_namespace')
    expected_runtime = {str(ROOT / 'manifests' / name): digest
                        for name, digest in PARENT_RUNTIME_SHA.items()}
    expected_lock = dict(zip(('dev','ino','uid','gid','mode','nlink','bytes'), LOCK_EXPECTED))
    if (set(baseline) != {'schema','captured_utc','capture_mode','receipt_source_sha256',
            'recovery_execution_fact_report','recovery_postexecution_evidence','formal_namespace',
            'prepared_tree','runtime_sha256','preserved_v4_authority','lock_receipt',
            'source_build_authorized'}
            or baseline.get('schema') != 'm9-source-build-v5-parent-namespace-evidence-v1'
            or baseline.get('capture_mode') != 'root-fixed-python3.9.23-I-S-B-shared-budget-lock-double-capture'
            or baseline.get('receipt_source_sha256') != RECEIPTS_SHA
            or baseline.get('recovery_execution_fact_report') != {'path':str(FACT),'sha256':FACT_SHA}
            or baseline.get('recovery_postexecution_evidence') != {'path':str(RECOVERY_EVIDENCE),'sha256':RECOVERY_EVIDENCE_SHA}
            or baseline.get('runtime_sha256') != expected_runtime
            or baseline.get('prepared_tree') != {'path':str(PREPARED),'count':5319,
                'canonical_sha256':PREPARED_SHA,'second_capture_equal':True}
            or baseline.get('preserved_v4_authority') != PRESERVED_V4_AUTHORITY
            or baseline.get('lock_receipt') != expected_lock
            or baseline.get('source_build_authorized') is not False
            or not isinstance(baseline.get('captured_utc'), str)
            or not isinstance(formal, dict) or set(formal) != {'count','canonical_sha256',
                'canonical_json_bytes','canonical_json_gzip_bytes','canonical_json_gzip_base64',
                'second_capture_equal'}
            or formal.get('count') != 301 or formal.get('canonical_sha256') != PARENT_FORMAL_SHA
            or not formal.get('second_capture_equal')
            or not isinstance(formal.get('canonical_json_gzip_base64'), str)):
        raise SystemExit('v5 parent namespace envelope differs')
    try:
        compressed = base64.b64decode(formal['canonical_json_gzip_base64'], validate=True)
        raw = gzip.decompress(compressed)
        value = json.loads(raw)
    except Exception as exc:
        raise SystemExit('v5 parent namespace payload is invalid') from exc
    if (len(compressed) != formal.get('canonical_json_gzip_bytes')
            or len(raw) != formal.get('canonical_json_bytes')
            or sha(raw) != formal.get('canonical_sha256')
            or canonical(value) != formal.get('canonical_sha256')
            or len(value) != 301):
        raise SystemExit('v5 parent namespace identity differs')
    return value


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
    namespace = baseline_namespace(baseline)
    fields = {'path', 'dev', 'ino', 'uid', 'gid', 'mode', 'nlink', 'bytes',
              'mtime_ns', 'ctime_ns', 'kind', 'sha256'}
    for name in ROOT_ONLY_NAMES:
        path = str(ROOT / 'manifests' / name)
        value = namespace.get(path)
        if (not isinstance(value, dict) or set(value) != fields or value['path'] != path
                or value['kind'] != 'file' or (value['uid'],value['gid'],value['mode'],value['nlink']) != (0,0,0o600,1)
                or not isinstance(value['sha256'], str) or len(value['sha256']) != 64):
            raise SystemExit('fixed root-only receipt malformed or missing: ' + path)
        selected[path] = value
    return selected


def history_attestation(baseline):
    namespace = baseline_namespace(baseline)
    return canonical({'schema':'m9-source-build-history-attestation-v5',
        'baseline_sha256':EVIDENCE_SHA, 'root_only':root_only_receipts(baseline),
        'root_private':{k:v for k,v in namespace.items() if k.startswith('/root/')}})


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
    expected = {k: v for k, v in baseline_namespace(baseline).items()
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
    if set(frozen) != {'schema', 'files'} or frozen['schema'] != 'm9-source-build-frozen-v5':
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
    read_bytes(RECOVERY_EVIDENCE, RECOVERY_EVIDENCE_SHA)
    read_bytes(FACT, FACT_SHA)
    read_bytes(OLD_INSTALL_VERDICT, OLD_INSTALL_VERDICT_SHA)
    read_bytes(OLD_V3_INSTALL_VERDICT, OLD_V3_INSTALL_VERDICT_SHA)
    read_bytes(OLD_V4_INSTALL_VERDICT, OLD_V4_INSTALL_VERDICT_SHA)


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
    if set(manifest) != {'schema', 'members'} or manifest['schema'] != 'm9-source-build-snapshot-v5':
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
    verify_verdict(json.loads(payloads[VERDICT.name]), 'm9-source-build-implementation-verdict-v5',
                   gate['frozen_sha256'], REPORT, gate['report_sha256'])
    return payloads


def validate_gate(gate):
    if (set(gate) != {'schema', 'status', 'scope', 'action', 'operation_id', 'nonce',
                     'frozen_sha256', 'snapshot_sha256', 'report_sha256', 'verdict_sha256',
                     'authorization_sha256', 'history_attestation_sha256', 'runtime'}
            or gate['schema'] != 'm9-source-build-readiness-v5'
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
            or state.get('recovered_from_source_build_wsl_shutdown') != RECOVERY_ID
            or workflow.get('recovered_from_source_build_wsl_shutdown') != RECOVERY_ID
            or tx['state'] != 'FAILED_COMMITTED' or tx['action'] != 'source_build'
            or tx['transaction_id'] != 'd52575f446d3c62f0fc93c3c65f3c959'
            or tx.get('recovery_id') != RECOVERY_ID
            or tx.get('reasons') != ['wsl_shutdown_external_interruption']
            or tx.get('elapsed_seconds') != 138.401802566
            or tx.get('elapsed_semantics') != 'conservative_wall_upper_bound_not_measured_cpu'
            or tx.get('exit_code') is not None or tx.get('timed_out') is not False):
        raise SystemExit('build preexecution terminal state mismatch')
    verify_prepared(reader)
    if require_permit:
        permit = json.loads(read_bytes(PERMIT, owner=(0, 1000, 0o640)))
        if (set(permit) != {'schema', 'gate_sha256', 'operation_id', 'nonce',
                           'report_sha256', 'verdict_sha256'}
                or permit['schema'] != 'm9-source-build-execution-permit-v5'
                or permit['gate_sha256'] != sha(raw)
                or permit['operation_id'] != OPERATION or permit['nonce'] != NONCE):
            raise SystemExit('build execution permit binding differs')
        report = read_bytes(INSTALL_REPORT, permit['report_sha256'])
        verdict = json.loads(read_bytes(INSTALL_VERDICT, permit['verdict_sha256']))
        verify_verdict(verdict, 'm9-source-build-installation-verdict-v5',
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
            or permit['schema'] != 'm9-source-build-execution-permit-v5'
            or permit['gate_sha256'] != sha(gate_raw)
            or permit['operation_id'] != OPERATION or permit['nonce'] != NONCE):
        raise SystemExit('static execution permit mismatch')
    fact = read_bytes(INSTALL_REPORT, permit['report_sha256'])
    verdict = json.loads(read_bytes(INSTALL_VERDICT, permit['verdict_sha256']))
    verify_verdict(verdict, 'm9-source-build-installation-verdict-v5',
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
        raise ValueError('v5 post-child authority validation failed: ' + str(exc)) from exc


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
            or receipt.get('v5_binding') != binding
            or consumed.get('schema_version') != 'm9-overlap-capability-v1'
            or consumed.get('state') != 'CONSUMED' or consumed.get('capability_id') != capability_id
            or consumed.get('transaction_id') != transaction_id
            or consumed.get('action') != 'source_build' or consumed.get('structure_id') is not None
            or consumed.get('bucket') != 'overlap_build'
            or consumed.get('forecast_bytes') != 4294967296
            or consumed.get('budget_bootstrap') != budget_bootstrap
            or consumed.get('budget_argv') != parent_argv or consumed.get('launcher_argv') != child_argv):
        raise ValueError('v5 launcher receipt/capability/authority mismatch')
    bootstrap = receipt.get('launcher_bootstrap')
    if (not isinstance(bootstrap, dict) or bootstrap.get('isolated') is not True
            or bootstrap.get('no_site') is not True or bootstrap.get('dont_write_bytecode') is not True
            or set(bootstrap.get('modules', {})) != {'argparse', 'hashlib', 'json', 'pathlib'}
            or bootstrap.get('python_executable') != str(PYTHON.resolve())):
        raise ValueError('v5 launcher bootstrap provenance mismatch')
    dependency = receipt.get('dependency_path')
    if (not isinstance(dependency, dict)
            or dependency.get('path') != str(PYTHON.parent.parent / 'lib/python3.9/site-packages')
            or dependency.get('added_after_capability') is not True
            or dependency.get('method') != 'sys.path.append'
            or dependency.get('site_addsitedir_called') is not False
            or dependency.get('pth_processed') is not False):
        raise ValueError('v5 source dependency provenance mismatch')
    sources = receipt.get('loaded_sources')
    if not isinstance(sources, dict) or set(sources) != {'m9_overlap_common', 'm9_openmx_build'}:
        raise ValueError('v5 loaded module closure mismatch')
    frozen = json.loads(read_bytes(OLD_OVERLAP_MANIFEST, OLD_MANIFESTS[OLD_OVERLAP_MANIFEST]))['files']
    for name, value in sources.items():
        if not isinstance(value, dict):
            raise ValueError('v5 invalid loaded source receipt')
        path = str(DRIVER.parent / (name + '.py'))
        fields = {'path', 'sha256', 'loader', 'origin', 'bytecode_consulted'}
        expected = frozen[path]
        if name == 'm9_openmx_build':
            fields.add('base_sha256'); expected = DRIVER_DERIVED_SHA
            if value.get('base_sha256') != DRIVER_BASE_SHA or frozen[path] != DRIVER_BASE_SHA:
                raise ValueError('v5 driver derivation provenance mismatch')
        if (not isinstance(value, dict) or set(value) != fields or value.get('path') != path
                or value.get('sha256') != expected or value.get('loader') != 'FrozenSourceLoader'
                or value.get('origin') != path or value.get('bytecode_consulted') is not False):
            raise ValueError('v5 actual loaded source mismatch: ' + name)
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
