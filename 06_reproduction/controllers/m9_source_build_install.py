"""Root mechanical installer and post-independent-audit execution permit.

Invoke only with the audited single-FD loader and six pinned hashes.
No build, deletion, automatic resumption, history rewrite or budget reset.
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
REPRO = PROJECT / '06_reproduction'
AUDITS = PROJECT / '08_audits'
SELF = REPRO / 'controllers/m9_source_build_install.py'
CONSUMER = REPRO / 'controllers/m9_source_build_consumer.py'
FROZEN = REPRO / 'manifests/m9_source_build_v1_frozen_hashes.json'
REPORT = AUDITS / 'M9_source_build_v1_implementation_audit.md'
VERDICT = AUDITS / 'M9_source_build_v1_implementation_verdict.json'


def pinned(path, expected):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        a = os.fstat(fd)
        with os.fdopen(os.dup(fd), 'rb') as stream:
            data = stream.read()
        b, linked = os.fstat(fd), os.lstat(path)
        keys = ('st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_mode', 'st_nlink',
                'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if (not stat.S_ISREG(a.st_mode) or a.st_nlink != 1 or len(data) != a.st_size
                or any(getattr(a, k) != getattr(b, k) or getattr(b, k) != getattr(linked, k) for k in keys)
                or hashlib.sha256(data).hexdigest() != expected):
            raise SystemExit('installer pinned bytes differ: ' + str(path))
        return data
    finally:
        os.close(fd)


def load_authority(args):
    if len(args) not in (6, 8) or args[1] not in ('preflight', 'install', 'permit'):
        raise SystemExit('expected self_sha action consumer_sha frozen_sha verdict_sha report_sha [fact_verdict_sha fact_report_sha]')
    self_sha, action, consumer_sha, frozen_sha, verdict_sha, report_sha = args[:6]
    if (action == 'permit') != (len(args) == 8):
        raise SystemExit('installation fact hashes are required only for permit')
    pinned(SELF, self_sha)
    consumer_bytes = pinned(CONSUMER, consumer_sha)
    frozen_bytes = pinned(FROZEN, frozen_sha)
    verdict_bytes = pinned(VERDICT, verdict_sha)
    report_bytes = pinned(REPORT, report_sha)
    frozen, verdict = json.loads(frozen_bytes), json.loads(verdict_bytes)
    if (frozen.get('schema') != 'm9-source-build-frozen-v1'
            or frozen.get('files', {}).get(str(SELF)) != self_sha
            or frozen.get('files', {}).get(str(CONSUMER)) != consumer_sha
            or verdict != {'schema': 'm9-source-build-implementation-verdict-v1',
                'status': 'PASS', 'blocking': 0, 'non_blocking': 0,
                'frozen_sha256': frozen_sha, 'report_path': str(REPORT), 'report_sha256': report_sha}):
        raise SystemExit('installer independent authority differs')
    spec = importlib.util.spec_from_file_location('m9_build_installer_consumer', CONSUMER)
    c = importlib.util.module_from_spec(spec); sys.modules[spec.name] = c
    exec(compile(consumer_bytes, str(CONSUMER), 'exec', dont_inherit=True), c.__dict__)
    c.verify_sources(frozen)
    c.verify_verdict(verdict, 'm9-source-build-implementation-verdict-v1', frozen_sha, REPORT, report_sha)
    return c, frozen, frozen_bytes, verdict_bytes, report_bytes


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def new_file(path, payload, mode=0o440):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, mode)
    try:
        os.fchown(fd, 0, 1000); os.fchmod(fd, mode)
        offset = 0
        while offset < len(payload):
            written = os.write(fd, payload[offset:])
            if written <= 0:
                raise OSError('short snapshot write')
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)


def preflight(c, frozen, installed):
    c.verify_sources(frozen)
    reader = c.receipts(installed=installed)
    baseline = json.loads(c.read_bytes(c.EVIDENCE, c.EVIDENCE_SHA))
    runtime = c.runtime_and_history(reader, baseline, installed=installed, private=True)
    c.verify_prepared(reader)
    base = c.read_bytes(c.OLD_BUDGET, c.BASE_SHA, (0, 1000, 0o440))
    derived = c.derive_budget(base)
    budget = c.load_bytes('m9_build_install_budget', c.SNAPSHOT / 'm9_budget_source_build.py', derived)
    state = budget.load_state()
    workflow = budget.load_workflow_state_budget()
    parsed = budget.build_parser().parse_args(c.require_argv(c.RUN_ARGV))
    if budget.validate_overlap_request(parsed, workflow) != ('source_build', 'overlap_build', 4294967296):
        raise SystemExit('build native request differs')
    if (budget.violations(state, 4294967296)
            or budget.effective_cpu_seconds(state, 'overlap_build') >= budget.CPU_LIMITS['overlap_build']):
        raise SystemExit('build installation budget forecast rejected')
    return reader, baseline, runtime, derived, budget


def install(c, frozen, frozen_bytes, verdict_bytes, report_bytes, do_write):
    staging = c.SNAPSHOT.with_name(c.SNAPSHOT.name + '.staging')
    for path in (c.SNAPSHOT, staging, c.GATE, c.GATE.with_suffix('.json.tmp'),
                 c.PERMIT, c.PERMIT.with_suffix('.json.tmp')):
        if os.path.lexists(path):
            raise SystemExit('non-pristine build installation; preserve and stop: ' + str(path))
    reader, baseline, runtime, derived, budget = preflight(c, frozen, False)
    payloads = {Path(p).name: c.read_bytes(Path(p), digest) for p, digest in frozen['files'].items()}
    payloads.update({c.FROZEN.name: frozen_bytes, c.VERDICT.name: verdict_bytes,
                     c.REPORT.name: report_bytes, 'm9_budget_source_build.py': derived})
    manifest = {'schema': 'm9-source-build-snapshot-v1', 'members': {
        name: {'bytes': len(data), 'sha256': c.sha(data)} for name, data in sorted(payloads.items())}}
    manifest_bytes = json_bytes(manifest)
    gate = {'schema': 'm9-source-build-readiness-v1', 'status': 'PASS', 'scope': c.SCOPE,
        'action': 'source_build', 'operation_id': c.OPERATION, 'nonce': c.NONCE,
        'frozen_sha256': c.sha(frozen_bytes), 'snapshot_sha256': c.sha(manifest_bytes),
        'report_sha256': c.sha(report_bytes), 'verdict_sha256': c.sha(verdict_bytes),
        'authorization_sha256': frozen['files'][str(c.AUTHORIZATION)], 'runtime': runtime}
    c.validate_gate(gate)
    if not do_write:
        print(json.dumps({'status': 'preflight_pass', 'gate_sha256': c.sha(json_bytes(gate)),
                          'snapshot_sha256': c.sha(manifest_bytes), 'writes': 0}, sort_keys=True))
        return
    # Last full checks occur under the same lock immediately before first write.
    if c.runtime_and_history(reader, baseline, private=True) != runtime:
        raise SystemExit('runtime changed before installation')
    c.verify_prepared(reader)
    staging.mkdir(mode=0o700); os.chown(staging, 0, 1000)
    for name, data in sorted(payloads.items()):
        new_file(staging / name, data)
    new_file(staging / 'snapshot_manifest.json', manifest_bytes)
    os.chmod(staging, 0o550); sync_directory(staging)
    if os.path.lexists(c.SNAPSHOT):
        raise SystemExit('snapshot appeared; preserve staging and stop')
    os.rename(staging, c.SNAPSHOT); sync_directory(c.SNAPSHOT.parent)
    c.runtime_and_history(reader, baseline, installed=True, private=True)
    if os.path.lexists(c.GATE) or os.path.lexists(c.GATE.with_suffix('.json.tmp')):
        raise SystemExit('gate namespace appeared; preserve snapshot and stop')
    budget.atomic_owned_durable_bytes(c.GATE, json_bytes(gate), expected_uid=0,
                                     expected_gid=1000, expected_mode=0o640)
    c.verify_gate(False)
    c.runtime_and_history(reader, baseline, installed=True, private=True)
    print(json.dumps({'status': 'build_snapshot_and_readiness_installed',
                      'gate_sha256': c.sha(c.read_bytes(c.GATE)),
                      'snapshot_sha256': c.sha(manifest_bytes), 'execution_permit_present': False}))


def permit(c, frozen, fact_verdict_sha, fact_report_sha):
    if os.path.lexists(c.PERMIT) or os.path.lexists(c.PERMIT.with_suffix('.json.tmp')):
        raise SystemExit('build permit already exists; do not reissue')
    report = c.read_bytes(c.INSTALL_REPORT, fact_report_sha)
    verdict = json.loads(c.read_bytes(c.INSTALL_VERDICT, fact_verdict_sha))
    frozen_sha = c.sha(c.read_bytes(c.FROZEN))
    c.verify_verdict(verdict, 'm9-source-build-installation-verdict-v1', frozen_sha,
                     c.INSTALL_REPORT, c.sha(report))
    reader, baseline, runtime, _, budget = preflight(c, frozen, True)
    gate = c.verify_gate(False)
    if gate['runtime'] != runtime:
        raise SystemExit('runtime changed before execution permit')
    value = {'schema': 'm9-source-build-execution-permit-v1',
             'gate_sha256': c.sha(c.read_bytes(c.GATE)), 'operation_id': c.OPERATION,
             'nonce': c.NONCE, 'report_sha256': fact_report_sha, 'verdict_sha256': fact_verdict_sha}
    budget.atomic_owned_durable_bytes(c.PERMIT, json_bytes(value),
        expected_uid=0, expected_gid=1000, expected_mode=0o640)
    c.verify_gate(True)
    c.runtime_and_history(reader, baseline, installed=True, private=True)
    print(json.dumps({'status': 'build_execution_permit_installed',
                      'permit_sha256': c.sha(c.read_bytes(c.PERMIT)), 'source_build_executed': False}))


def main():
    if os.geteuid() != 0 or not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        raise SystemExit('root isolated no-site/no-bytecode installer required')
    args = sys.argv[1:]
    c, frozen, frozen_bytes, verdict_bytes, report_bytes = load_authority(args)
    c.fixed_runtime()
    fd = os.open(c.LOCK, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX); c.lock_identity(fd)
        if args[1] == 'permit':
            permit(c, frozen, args[6], args[7])
        else:
            install(c, frozen, frozen_bytes, verdict_bytes, report_bytes, args[1] == 'install')
        c.lock_identity(fd)
    finally:
        os.close(fd)


if __name__ == '__main__':
    main()
