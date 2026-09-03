"""One-time mechanical issuance of the explicitly approved source_prepare record.

Does not invoke the adapter main or any source action. Never overwrites or retries.
"""
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
ROOT = Path('/home/evan-williams/deeph-m9')
SNAPSHOT = ROOT / 'controls/uid1000-consumer-py39-v2'
PYTHON = ROOT / 'env/deeph-v022/bin/python3.9'
ADAPTER = SNAPSHOT / 'm9_budget_uid1000_consumer.py'
CONTROLLER = SNAPSHOT / 'm9_budget.py'
PAYLOAD = PROJECT / '06_reproduction/manifests/m9_source_prepare_py39_fresh_authorization_payload.json'
RECORD = PROJECT / '08_audits/M9_source_prepare_py39_fresh_user_authorization.md'
FACT = PROJECT / '08_audits/M9_py39_consumer_gate_completion_execution_independent_audit.md'
EXPECTED = {
    ADAPTER: 'a47127b937ebb69584465ccbb00b0307c77a718ec312c6509aca7b228cec2afa',
    CONTROLLER: 'a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d',
    PAYLOAD: '62bf44207a3f3338fce3f8b4476a0b37be97f7587d2f07148aa3978b9014b4ab',
    RECORD: '258212b82ccf0fc6bcd23ce93486f692d2e092d11e502f8b09926f0575bbf368',
    FACT: '798ada7ed0c8835cc56b28d168188d61688e21d2ecdfacfb4d56ac6da660bcdc',
}
ARGV = ['run', '--consumer-operation-id', 'f9824f0eb63e41f19699c1114b13537e',
        '--bucket', 'none', '--cpu-bucket', 'overlap_build',
        '--forecast-bytes', '1073741824', '--overlap-operation',
        '--overlap-action', 'source_prepare', '--config',
        str(PROJECT / '06_reproduction/configs/m9_overlap_only_contract.json')]


def exact_read(path, digest):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        with os.fdopen(os.dup(fd), 'rb') as stream:
            payload = stream.read()
        after, linked = os.fstat(fd), os.lstat(path)
        keys = ('st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_mode', 'st_nlink',
                'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or any(getattr(before, k) != getattr(after, k)
                       or getattr(after, k) != getattr(linked, k) for k in keys)
                or len(payload) != after.st_size
                or hashlib.sha256(payload).hexdigest() != digest):
            raise SystemExit('fixed source receipt mismatch: ' + str(path))
        if path.parent == SNAPSHOT and (
                before.st_uid, before.st_gid, stat.S_IMODE(before.st_mode)) != (0, 1000, 0o440):
            raise SystemExit('snapshot member metadata mismatch')
        return payload
    finally:
        os.close(fd)


VERIFY = """import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('issued_auth_consumer',sys.argv[1])
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
r=c.verify_consumer_gate() if sys.argv[2]=='before' else c.verify_source_prepare_authorization(json.loads(sys.argv[3]))
m=c.original_controller();state=m.load_state();workflow=m.load_workflow_state_budget()
op,delegated=c.source_prepare_adapter_argv(json.loads(sys.argv[3]))
args=m.build_parser().parse_args(delegated)
request=m.validate_overlap_request(args,workflow)
if m.violations(state,1073741824) or m.effective_cpu_seconds(state,'overlap_build')>=m.CPU_LIMITS['overlap_build']:
    raise SystemExit('budget precheck rejected issuance')
print(json.dumps({'gate':r['gate'],'receipt':r['gate_receipt'],'runtime':c.consumer_runtime_receipts(),'request':request},sort_keys=True))
"""


def verify_as_user(phase):
    result = subprocess.run(['/usr/sbin/runuser', '-u', 'evan-williams', '--',
        str(PYTHON), '-I', '-S', '-B', '-c', VERIFY, str(ADAPTER), phase,
        json.dumps(ARGV)], capture_output=True, text=True, check=True)
    if result.stderr:
        raise SystemExit('UID1000 verifier emitted stderr: ' + result.stderr)
    return json.loads(result.stdout)


def main():
    if (os.geteuid() != 0 or sys.version_info[:3] != (3, 9, 23)
            or Path(sys.executable).resolve() != PYTHON.resolve()
            or not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode)):
        raise SystemExit('requires root and frozen isolated Python 3.9.23')
    metadata = os.lstat(SNAPSHOT)
    if (not stat.S_ISDIR(metadata.st_mode)
            or (metadata.st_uid, metadata.st_gid, stat.S_IMODE(metadata.st_mode)) != (0, 1000, 0o550)):
        raise SystemExit('snapshot root metadata mismatch')
    sources = {path: exact_read(path, digest) for path, digest in EXPECTED.items()}
    spec = importlib.util.spec_from_file_location('issuance_frozen_budget', CONTROLLER)
    m9 = importlib.util.module_from_spec(spec)
    exec(compile(sources[CONTROLLER], str(CONTROLLER), 'exec'), m9.__dict__)
    lock_fd = os.open(m9.LOCK_PATH, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        lock = os.fstat(lock_fd)
        if (lock.st_dev, lock.st_ino, lock.st_uid, lock.st_gid,
                stat.S_IMODE(lock.st_mode), lock.st_nlink, lock.st_size) != (2096, 50700, 1000, 1000, 0o644, 1, 0):
            raise SystemExit('original budget lock identity mismatch')
        auth_path = ROOT / 'manifests/overlap_source_prepare_py39_single_run_authorization.json'
        if os.path.lexists(auth_path) or os.path.lexists(auth_path.with_suffix('.json.tmp')):
            raise SystemExit('authorization namespace already exists; no overwrite or retry')
        for path, digest in EXPECTED.items():
            exact_read(path, digest)
        for name, digest in [
            ('m9_source_prepare_py39_uid1000_consumer_frozen_hashes.json', '765dcf5c09c90ae8d9c2789df1c16f379eca397f18d1dade55167c1b5df207e7'),
            ('m9_overlap_py39_recovery_frozen_hashes.json', '8a3166d61c4f777424f0509ae2d9aae3cc0a6c7f90a725fb9126f5cc25147e3a')]:
            manifest = json.loads(exact_read(PROJECT / '06_reproduction/manifests' / name, digest))
            for path, member_hash in manifest['files'].items():
                exact_read(Path(path), member_hash)
        before = verify_as_user('before')
        value = json.loads(sources[PAYLOAD])
        if (value['consumer_gate_sha256'] != before['receipt']['sha256']
                or value['active_overlap_gate_sha256'] != before['gate']['active_overlap_gate_sha256']
                or value['runtime_sha256'] != m9.canonical_hash(before['runtime'])
                or before['gate']['runtime'] != before['runtime']):
            raise SystemExit('authorization runtime binding mismatch')
        linked = os.lstat(m9.LOCK_PATH)
        if (linked.st_dev, linked.st_ino) != (lock.st_dev, lock.st_ino):
            raise SystemExit('budget lock path changed')
        m9.atomic_owned_durable_bytes(auth_path, sources[PAYLOAD],
            expected_uid=0, expected_gid=1000, expected_mode=0o640)
        receipt, installed, payload = m9.read_d018_control_json(auth_path)
        if installed != value or payload != sources[PAYLOAD]:
            raise SystemExit('issued authorization differs; retain evidence and stop')
        after = verify_as_user('after')
        if after != before:
            raise SystemExit('runtime changed during issuance; retain evidence and stop')
        print(json.dumps({'status': 'authorization_issued_and_verified',
            'receipt': receipt, 'operation_id': value['operation_id'],
            'source_prepare_executed': False}, sort_keys=True))
    finally:
        os.close(lock_fd)


if __name__ == '__main__':
    main()
