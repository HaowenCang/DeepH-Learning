"""Synthetic source-build controls; never runs a compiler or formal action."""
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

REPRO = Path(__file__).resolve().parents[1]
CONSUMER_PATH = REPRO / 'controllers/m9_source_build_v2_consumer.py'
INSTALL_PATH = REPRO / 'controllers/m9_source_build_v2_install.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


c = load('source_build_test_consumer', CONSUMER_PATH)
i = load('source_build_test_installer', INSTALL_PATH)
REAL_RECEIPTS = c.read_bytes(c.RECEIPTS, c.RECEIPTS_SHA)
REAL_CONSUMER = c.read_bytes(CONSUMER_PATH)
BASE = c.read_bytes(c.OLD_BUDGET, c.BASE_SHA)


def write(path, payload, mode=0o644, uid=0, gid=1000):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    os.chown(path, uid, gid); os.chmod(path, mode)


def jwrite(path, value, mode=0o644):
    write(path, i.json_bytes(value), mode)


class Fixture:
    def __init__(self, installed=True):
        self.temporary = tempfile.TemporaryDirectory(prefix='m9-build-unit-')
        self.base = Path(self.temporary.name); os.chmod(self.base, 0o755)
        self.stack = contextlib.ExitStack()
        root = self.base / 'runtime'; project = self.base / 'project'
        for p in [root, root / 'controls', root / 'manifests', project]:
            p.mkdir(parents=True, exist_ok=True); os.chown(p, 0, 1000); os.chmod(p, 0o755)
        self.overrides = {'PROJECT': project, 'ROOT': root, 'SNAPSHOT': root / 'controls/source-build-v2',
            'GATE': root / 'manifests/source_build_v2_gate.json',
            'PERMIT': root / 'manifests/source_build_v2_execution_permit.json',
            'LOCK': root / 'manifests/budget.lock', 'PREPARED': root / 'software/prepared',
            'RETIRED': root / 'software/retired'}
        names = ('PROJECT_CONSUMER', 'PROJECT_INSTALLER', 'FROZEN', 'AUTHORIZATION', 'WORK',
                 'TEST', 'REPORT', 'VERDICT', 'INSTALL_REPORT', 'INSTALL_VERDICT', 'EVIDENCE',
                 'FACT', 'RECEIPTS', 'OLD_CONSUMER_MANIFEST', 'OLD_OVERLAP_MANIFEST',
                 'OLD_BUILD_MANIFEST', 'OLD_INSTALL_VERDICT', 'CONTRACT')
        self.overrides.update({name: project / getattr(c, name).name for name in names})
        for name, value in self.overrides.items():
            self.stack.enter_context(mock.patch.object(c, name, value))
        sources = {getattr(c, name) for name in ('PROJECT_CONSUMER', 'PROJECT_INSTALLER', 'TEST',
            'WORK', 'AUTHORIZATION', 'EVIDENCE', 'FACT', 'RECEIPTS', 'OLD_CONSUMER_MANIFEST', 'OLD_OVERLAP_MANIFEST',
            'OLD_BUILD_MANIFEST', 'OLD_INSTALL_VERDICT')}
        self.stack.enter_context(mock.patch.object(c, 'SOURCE_PATHS', sources))
        for p in sources:
            write(p, b'fixture source\n')
        write(c.RECEIPTS, REAL_RECEIPTS)
        write(c.PROJECT_CONSUMER, REAL_CONSUMER)
        for p in (c.OLD_CONSUMER_MANIFEST, c.OLD_OVERLAP_MANIFEST, c.OLD_BUILD_MANIFEST):
            jwrite(p, {'files': {}})
        old_manifests = {p: c.sha(p.read_bytes()) for p in (c.OLD_CONSUMER_MANIFEST, c.OLD_OVERLAP_MANIFEST, c.OLD_BUILD_MANIFEST)}
        self.stack.enter_context(mock.patch.object(c, 'OLD_MANIFESTS', old_manifests))
        self.stack.enter_context(mock.patch.object(c, 'OLD_INSTALL_VERDICT_SHA', c.sha(c.OLD_INSTALL_VERDICT.read_bytes())))
        self.reader = c.receipts(False)
        write(c.PREPARED / 'hdf5/configure', b'configure source\n', 0o755, 1000, 1000)
        write(c.PREPARED / 'openmx/makefile', b'CC=gcc\n', 0o644, 1000, 1000)
        write(c.RETIRED / 'failure.txt', b'historical failure\n', 0o644, 1000, 1000)
        self.stack.enter_context(mock.patch.object(c, 'PREPARED_SHA', c.canonical(self.reader.capture_tree(c.PREPARED))))
        self.stack.enter_context(mock.patch.object(c, 'RETIRED_SHA', c.canonical(self.reader.capture_tree(c.RETIRED))))
        self.stack.enter_context(mock.patch.object(c, 'FORBIDDEN_PRODUCTS', [root / x for x in (
            'env/hdf5', 'manifests/build.json', 'logs/overlap-build', 'runs/overlap-only-openmx')]))
        state = {'hard_stopped': False, 'active_overlap_transaction': None,
                 'wall_clock_policy': {'mode': 'UNLIMITED'}}
        workflow = {'schema_version':'m9-overlap-workflow-state-v1',
                    'hard_stopped': False, 'active_transaction': None, 'stage': 'SOURCES_PREPARED'}
        tx = {'state': 'SUCCESS_COMMITTED', 'action': 'source_prepare',
              'transaction_id': 'dc75dda112af553377a697f629801782'}
        for n, v in [('budget_state.json', state), ('overlap_workflow_state.json', workflow),
                     ('overlap_transaction.json', tx), ('openmx_official_3.9.9_tree_manifest.json', {})]:
            jwrite(root / 'manifests' / n, v)
        write(root / 'manifests/budget_ledger.jsonl', b'{"historical":true}\n')
        write(c.LOCK, b'', 0o644, 1000, 1000)
        lock_stat = c.LOCK.stat()
        self.stack.enter_context(mock.patch.object(c, 'LOCK_EXPECTED',
            (lock_stat.st_dev,lock_stat.st_ino,1000,1000,0o644,1,0)))
        mutable = {str(root / 'manifests' / n) for n in ('budget_state.json', 'overlap_workflow_state.json',
            'overlap_transaction.json', 'budget_ledger.jsonl', 'openmx_official_3.9.9_tree_manifest.json')}
        self.stack.enter_context(mock.patch.object(c, 'MUTABLE_RUNTIME', mutable))
        formal = {}
        # Reproduce the actual eight preserved root-only history objects.
        for name in ["overlap_source_control_recovery.test-artifact.retired.json","overlap_source_control_recovery_gate.closed-set-invalid.retired.json","overlap_source_control_recovery_gate.json","overlap_source_control_recovery_gate.pre-ledger-fix.retired.json","overlap_source_control_recovery_gate.pre-lock-mode-refresh.retired.json","overlap_source_control_test_artifact_cleanup.json","overlap_source_control_test_artifact_retirement.json","overlap_source_control_test_cleanup_gate.json"]:
            write(root / 'manifests' / name, b'root-only historical evidence\n', 0o600, 0, 0)
        for p in [root / 'controls', root / 'manifests']:
            formal.update(self.reader.capture_tree(p))
        self.baseline = {'formal_namespace': formal}
        jwrite(c.EVIDENCE, self.baseline)
        self.stack.enter_context(mock.patch.object(c, 'EVIDENCE_SHA', c.sha(c.EVIDENCE.read_bytes())))
        self.stack.enter_context(mock.patch.object(c, 'FACT_SHA', c.sha(c.FACT.read_bytes())))
        self.frozen = {'schema': 'm9-source-build-frozen-v2', 'files': {
            str(p): c.sha(p.read_bytes()) for p in c.SOURCE_PATHS}}
        jwrite(c.FROZEN, self.frozen)
        write(c.REPORT, b'independent implementation PASS\n')
        self.verdict = {'schema': 'm9-source-build-implementation-verdict-v2', 'status': 'PASS',
            'blocking': 0, 'non_blocking': 0, 'frozen_sha256': c.sha(c.FROZEN.read_bytes()),
            'report_path': str(c.REPORT), 'report_sha256': c.sha(c.REPORT.read_bytes())}
        jwrite(c.VERDICT, self.verdict)
        self.runtime = {k: formal[k] for k in sorted(c.MUTABLE_RUNTIME)}
        if not installed:
            return
        self.payloads = {p.name: p.read_bytes() for p in c.SOURCE_PATHS | {c.FROZEN, c.REPORT, c.VERDICT}}
        self.payloads['m9_budget_source_build.py'] = c.derive_budget(BASE)
        c.SNAPSHOT.mkdir(mode=0o755); os.chown(c.SNAPSHOT, 0, 1000)
        for name, data in self.payloads.items():
            i.new_file(c.SNAPSHOT / name, data)
        snapshot = {'schema': 'm9-source-build-snapshot-v2', 'members': {
            name: {'bytes': len(data), 'sha256': c.sha(data)} for name, data in self.payloads.items()}}
        i.new_file(c.SNAPSHOT / 'snapshot_manifest.json', i.json_bytes(snapshot))
        os.chmod(c.SNAPSHOT, 0o550)
        self.gate = {'schema': 'm9-source-build-readiness-v2', 'status': 'PASS', 'scope': c.SCOPE,
            'action': 'source_build', 'operation_id': c.OPERATION, 'nonce': c.NONCE,
            'frozen_sha256': c.sha(c.FROZEN.read_bytes()),
            'snapshot_sha256': c.sha(i.json_bytes(snapshot)),
            'report_sha256': c.sha(c.REPORT.read_bytes()), 'verdict_sha256': c.sha(c.VERDICT.read_bytes()),
            'authorization_sha256': c.sha(c.AUTHORIZATION.read_bytes()),
            'history_attestation_sha256':c.history_attestation(self.baseline), 'runtime': self.runtime}
        jwrite(c.GATE, self.gate, 0o640)
        write(c.INSTALL_REPORT, b'independent installation PASS\n')
        iv = dict(self.verdict, schema='m9-source-build-installation-verdict-v2',
                  report_path=str(c.INSTALL_REPORT), report_sha256=c.sha(c.INSTALL_REPORT.read_bytes()))
        jwrite(c.INSTALL_VERDICT, iv)
        self.permit = {'schema': 'm9-source-build-execution-permit-v2',
            'gate_sha256': c.sha(c.GATE.read_bytes()), 'operation_id': c.OPERATION, 'nonce': c.NONCE,
            'report_sha256': c.sha(c.INSTALL_REPORT.read_bytes()),
            'verdict_sha256': c.sha(c.INSTALL_VERDICT.read_bytes())}
        jwrite(c.PERMIT, self.permit, 0o640)

    def close(self):
        self.stack.close(); self.temporary.cleanup()


class BuildTests(unittest.TestCase):
    def fixture(self, installed=True):
        f = Fixture(installed); self.addCleanup(f.close); return f

    def mechanical_install(self, f, do_write=True):
        # Replace only the formal budget preflight and private-root location.
        # All snapshot writes, namespace checks and consumer verification are real.
        budget = c.load_bytes('build_test_mechanical_budget', c.OLD_BUDGET, c.derive_budget(BASE))
        original_history = c.runtime_and_history
        def public_history(reader, baseline, installed=False, private=False):
            return original_history(reader, baseline, installed=installed, private=False)
        preflight = (f.reader, f.baseline, f.runtime, c.derive_budget(BASE), budget)
        with mock.patch.object(i, 'preflight', return_value=preflight), \
             mock.patch.object(c, 'runtime_and_history', side_effect=public_history):
            i.install(c, f.frozen, c.FROZEN.read_bytes(), c.VERDICT.read_bytes(), c.REPORT.read_bytes(), do_write)

    def test_real_mechanical_install_and_pristine_replay_rejection(self):
        f = self.fixture(False); self.mechanical_install(f)
        self.assertFalse(c.PERMIT.exists())
        self.assertEqual(c.verify_gate(False)['scope'], c.SCOPE)
        with self.assertRaises(FileNotFoundError): c.verify_gate(True)
        before = f.reader.capture_tree(c.ROOT)
        with self.assertRaises(SystemExit): self.mechanical_install(f)
        self.assertEqual(before, f.reader.capture_tree(c.ROOT))

    def test_real_mechanical_preflight_writes_nothing(self):
        f = self.fixture(False); before = f.reader.capture_tree(f.base)
        self.mechanical_install(f, False)
        self.assertEqual(before, f.reader.capture_tree(f.base))

    def test_mechanical_interruption_preserves_staging_and_refuses_retry(self):
        f = self.fixture(False)
        with mock.patch.object(i, 'new_file', side_effect=OSError('synthetic interruption')):
            with self.assertRaises(OSError): self.mechanical_install(f)
        staging = c.SNAPSHOT.with_name(c.SNAPSHOT.name + '.staging')
        self.assertTrue(staging.is_dir()); self.assertFalse(c.GATE.exists())
        before = f.reader.capture_tree(c.ROOT)
        with self.assertRaises(SystemExit): self.mechanical_install(f)
        self.assertEqual(before, f.reader.capture_tree(c.ROOT))

    def test_mechanical_permit_requires_fact_and_rejects_reissue(self):
        f = self.fixture(False); self.mechanical_install(f)
        with self.assertRaises(FileNotFoundError): i.permit(c, f.frozen, '0'*64, '0'*64)
        write(c.INSTALL_REPORT, b'independent fixture installation PASS\n')
        verdict = dict(f.verdict, schema='m9-source-build-installation-verdict-v2',
                       report_path=str(c.INSTALL_REPORT), report_sha256=c.sha(c.INSTALL_REPORT.read_bytes()))
        jwrite(c.INSTALL_VERDICT, verdict)
        budget = c.load_bytes('build_test_permit_budget', c.OLD_BUDGET, c.derive_budget(BASE))
        original_history = c.runtime_and_history
        with mock.patch.object(i, 'preflight', return_value=(f.reader,f.baseline,f.runtime,None,budget)), \
             mock.patch.object(c, 'runtime_and_history', side_effect=lambda reader,baseline,installed=False,private=False:
                               original_history(reader,baseline,installed,False)):
            i.permit(c, f.frozen, c.sha(c.INSTALL_VERDICT.read_bytes()), verdict['report_sha256'])
        c.verify_gate(True)
        before = f.reader.capture_tree(c.ROOT)
        with self.assertRaises(SystemExit):
            i.permit(c, f.frozen, c.sha(c.INSTALL_VERDICT.read_bytes()), verdict['report_sha256'])
        self.assertEqual(before, f.reader.capture_tree(c.ROOT))

    def test_installer_authority_bad_hash_never_loads_consumer(self):
        with mock.patch.object(i.importlib.util, 'module_from_spec', side_effect=AssertionError('untrusted import')):
            with self.assertRaises(SystemExit): i.load_authority(['0'*64,'install',*(['0'*64]*4)])

    def test_exact_derivation_and_budget_other_bytes_unchanged(self):
        derived = c.derive_budget(BASE)
        self.assertEqual(c.sha(derived), c.DERIVED_SHA)
        self.assertEqual(derived.replace(c.NEW_BLOCK, c.OLD_BLOCK, 1), BASE)
        with self.assertRaises(SystemExit): c.derive_budget(BASE + b'\n')

    def test_unique_argv_real_parser_and_validator(self):
        b = c.load_bytes('build_parser_real', c.OLD_BUDGET, c.derive_budget(BASE))
        args = b.build_parser().parse_args(c.require_argv(c.RUN_ARGV))
        self.assertEqual(args.command, [])
        self.assertEqual(b.validate_overlap_request(args, {'stage': 'SOURCES_PREPARED', 'hard_stopped': False}),
                         ('source_build', 'overlap_build', 4294967296))

    def test_reject_argv_variants(self):
        variants = [[], ['verify'], c.RUN_ARGV + ['--'], c.RUN_ARGV + ['--log', '/tmp/x'],
            c.RUN_ARGV + ['--structure-id', '500'], c.RUN_ARGV + ['--bucket', 'none'],
            [x.replace('source_build', 'source_prepare') for x in c.RUN_ARGV],
            [x.replace('4294967296', '1073741824') for x in c.RUN_ARGV],
            [x.replace('--overlap-operation', '--overlap-oper') for x in c.RUN_ARGV],
            [x.replace('none', 'training') for x in c.RUN_ARGV]]
        for argv in variants:
            with self.subTest(argv=argv), self.assertRaises(SystemExit): c.require_argv(argv)

    def test_complete_real_fixture_pass(self):
        f = self.fixture(); self.assertEqual(c.verify_gate(True), f.gate)

    def test_missing_permit_and_wrong_scope(self):
        f = self.fixture(); c.PERMIT.unlink()
        self.assertEqual(c.verify_gate(False), f.gate)
        with self.assertRaises(FileNotFoundError): c.verify_gate(True)
        jwrite(c.GATE, dict(f.gate, scope='ALLOW_EXACTLY_ONE_SOURCE_PREPARE'), 0o640)
        with self.assertRaises(SystemExit): c.verify_gate(False)

    def test_gate_extra_field_and_wrong_nonce(self):
        f = self.fixture()
        for gate in [dict(f.gate, extra=True), dict(f.gate, nonce='0' * 64)]:
            jwrite(c.GATE, gate, 0o640)
            with self.assertRaises(SystemExit): c.verify_gate(False)

    def test_snapshot_extra_file(self):
        self.fixture(); i.new_file(c.SNAPSHOT / 'extra.py', b'pass\n')
        with self.assertRaises(SystemExit): c.verify_gate(False)

    def test_snapshot_changed_same_size_bytes(self):
        self.fixture(); p = c.SNAPSHOT / c.WORK.name
        write(p, b'changed source\n', 0o440)
        with self.assertRaises(SystemExit): c.verify_gate(False)

    def test_snapshot_symlink(self):
        self.fixture(); p = c.SNAPSHOT / c.WORK.name; p.unlink(); p.symlink_to(c.WORK)
        with self.assertRaises((SystemExit, OSError)): c.verify_gate(False)

    def test_snapshot_hardlink(self):
        self.fixture(); os.link(c.SNAPSHOT / c.WORK.name, c.SNAPSHOT.parent / 'other-link')
        with self.assertRaises(SystemExit): c.verify_gate(False)

    def test_snapshot_permission_drift(self):
        self.fixture(); os.chmod(c.SNAPSHOT / c.WORK.name, 0o644)
        with self.assertRaises(SystemExit): c.verify_gate(False)

    def test_hdf_source_drift(self):
        self.fixture(); write(c.PREPARED / 'hdf5/configure', b'changed\n', 0o755, 1000, 1000)
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_extra_prepared_file(self):
        self.fixture(); write(c.PREPARED / 'extra', b'X', 0o644, 1000, 1000)
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_prepared_same_bytes_new_inode_rejected(self):
        self.fixture(); p=c.PREPARED/'hdf5/configure'; b=p.read_bytes(); p.unlink(); write(p,b,0o755,1000,1000)
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_retired_history_drift(self):
        self.fixture(); write(c.RETIRED / 'failure.txt', b'changed failure\n')
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_preexisting_products_rejected(self):
        for index in range(4):
            with self.subTest(index=index):
                f=Fixture()
                try:
                    c.FORBIDDEN_PRODUCTS[index].mkdir(parents=True)
                    with self.assertRaises(SystemExit): c.verify_gate(True)
                finally: f.close()

    def test_runtime_nonterminal_and_replay_rejected(self):
        self.fixture(); p=c.ROOT/'manifests/overlap_workflow_state.json'
        jwrite(p, {'stage':'BUILD_PASSED','hard_stopped':False,'active_transaction':None})
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_authorization_record_drift(self):
        self.fixture(); write(c.AUTHORIZATION,b'broadened scope\n')
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_permit_wrong_gate_hash(self):
        f=self.fixture(); jwrite(c.PERMIT,dict(f.permit,gate_sha256='0'*64),0o640)
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_installed_report_hash_drift(self):
        self.fixture(); write(c.INSTALL_REPORT,b'not a PASS\n')
        with self.assertRaises(SystemExit): c.verify_gate(True)

    def test_verdict_bool_is_not_zero_issue_integer(self):
        f=self.fixture(); v=dict(f.verdict,blocking=False)
        with self.assertRaises(SystemExit):
            c.verify_verdict(v,v['schema'],v['frozen_sha256'],c.REPORT,v['report_sha256'])

    def test_locked_first_write_revalidates_real_fixture(self):
        self.fixture(); calls=[]
        budget=types.SimpleNamespace(atomic_json=lambda p,v:calls.append((p,v)))
        c.guard_budget(budget)
        self.assertEqual(budget.verify_unlimited_wall_clock_execution_fact_gate()['gate']['scope'], c.SCOPE)
        write(c.PREPARED/'hdf5/configure',b'drift after first read\n',0o755,1000,1000)
        with self.assertRaises(SystemExit): budget.atomic_json(c.ROOT/'manifests/overlap_transaction.json',{})
        self.assertEqual(calls,[])

    def test_real_budget_incomplete_transaction_branch_is_locked_zero_write(self):
        f = self.fixture()
        b = c.load_bytes('build_real_incomplete_branch', c.OLD_BUDGET, c.derive_budget(BASE))
        b.LOCK_PATH = c.LOCK
        b.STATE_PATH = c.ROOT / 'manifests/budget_state.json'
        b.OVERLAP_WORKFLOW_STATE = c.ROOT / 'manifests/overlap_workflow_state.json'
        b.OVERLAP_TRANSACTION = c.ROOT / 'manifests/overlap_transaction.json'
        # A real incomplete on-disk transaction reaches native hard_stop_both.
        jwrite(b.OVERLAP_TRANSACTION, {'state':'PREPARED','child_pid':None})
        before = f.reader.capture_tree(c.ROOT)
        args = b.build_parser().parse_args(c.require_argv(c.RUN_ARGV))
        verifier = c.verify_gate
        locked = []
        def checked_verifier(require_permit=True):
            fd = os.open(c.LOCK, os.O_RDWR)
            try:
                with self.assertRaises(BlockingIOError):
                    c.fcntl.flock(fd, c.fcntl.LOCK_EX | c.fcntl.LOCK_NB)
                locked.append(True)
            finally: os.close(fd)
            return verifier(require_permit)
        with mock.patch.object(b.os, 'geteuid', return_value=1000), \
             mock.patch.object(b, 'isolated_bootstrap_provenance', return_value={}), \
             mock.patch.object(b, 'atomic_json', side_effect=AssertionError('native write reached')) as mutator, \
             mock.patch.object(b.subprocess, 'Popen', side_effect=AssertionError('child launched')), \
             mock.patch.object(c, 'verify_gate', side_effect=checked_verifier):
            c.guard_budget(b)
            with self.assertRaises(SystemExit): b.command_overlap_run(args)
            mutator.assert_not_called()
        self.assertEqual(locked, [True])
        self.assertEqual(before, f.reader.capture_tree(c.ROOT))

    def test_first_write_guard_then_reuse_native_transaction_writes(self):
        self.fixture(); calls=[]
        budget=types.SimpleNamespace(atomic_json=lambda p,v:calls.append((p,v))); c.guard_budget(budget)
        budget.atomic_json(Path('synthetic-only'),{})
        with mock.patch.object(c,'verify_gate',side_effect=AssertionError('must not check old runtime after write')):
            budget.atomic_json(Path('synthetic-only-2'),{})
        self.assertEqual(len(calls),2)

    def test_source_entrypoint_refuses_project_path(self):
        with self.assertRaises(SystemExit): c.main()

    def test_new_file_refuses_overwrite_and_keeps_bytes(self):
        f=self.fixture(); p=f.base/'new'; i.new_file(p,b'first')
        with self.assertRaises(FileExistsError): i.new_file(p,b'second')
        self.assertEqual(p.read_bytes(),b'first')

    def run_uid1000(self, f, command='verify-function'):
        path_values={k:str(v) for k,v in f.overrides.items()}
        settings={'paths':path_values,'SOURCE_PATHS':[str(p) for p in c.SOURCE_PATHS],
            'OLD_MANIFESTS':{str(p):v for p,v in c.OLD_MANIFESTS.items()},
            'MUTABLE_RUNTIME':list(c.MUTABLE_RUNTIME),'FORBIDDEN_PRODUCTS':[str(p) for p in c.FORBIDDEN_PRODUCTS],
            'PREPARED_SHA':c.PREPARED_SHA,'RETIRED_SHA':c.RETIRED_SHA,'EVIDENCE_SHA':c.EVIDENCE_SHA,'FACT_SHA':c.FACT_SHA,
            'OLD_INSTALL_VERDICT_SHA':c.OLD_INSTALL_VERDICT_SHA,'LOCK_EXPECTED':c.LOCK_EXPECTED}
        code="""import importlib.util,json,os,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('fixture_real_uid',sys.argv[1]);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
x=json.loads(sys.argv[2])
for k,v in x['paths'].items():setattr(c,k,Path(v))
c.SOURCE_PATHS={Path(p) for p in x['SOURCE_PATHS']};c.OLD_MANIFESTS={Path(p):v for p,v in x['OLD_MANIFESTS'].items()}
c.MUTABLE_RUNTIME=set(x['MUTABLE_RUNTIME']);c.FORBIDDEN_PRODUCTS=[Path(p) for p in x['FORBIDDEN_PRODUCTS']]
for k in ['PREPARED_SHA','RETIRED_SHA','EVIDENCE_SHA','FACT_SHA','OLD_INSTALL_VERDICT_SHA']:setattr(c,k,x[k])
assert os.geteuid()==1000
c.LOCK_EXPECTED=tuple(x['LOCK_EXPECTED'])
if sys.argv[3]=='verify-function':c.verify_gate(True)
else:
 command=sys.argv[3];sys.argv=[str(c.SNAPSHOT/c.PROJECT_CONSUMER.name),command];c.main()
print('actual_uid1000_fixture_PASS')
"""
        result=subprocess.run(['/usr/sbin/runuser','-u','evan-williams','--',sys.executable,'-I','-S','-B',
            '-c',code,str(c.SNAPSHOT/c.PROJECT_CONSUMER.name),json.dumps(settings),command],capture_output=True,text=True)
        return result

    def test_real_uid1000_verifier(self):
        f=self.fixture(); result=self.run_uid1000(f)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('actual_uid1000_fixture_PASS',result.stdout)

    def test_real_installed_main_ready_and_missing_permit_exact_failure_zero_write(self):
        f=self.fixture(); c.PERMIT.unlink()
        before=f.reader.capture_tree(c.ROOT)
        ready=self.run_uid1000(f,'verify-ready')
        self.assertEqual(ready.returncode,0,ready.stderr)
        missing=self.run_uid1000(f,'verify-execution')
        self.assertEqual(missing.returncode,1)
        self.assertIn('FileNotFoundError',missing.stderr)
        self.assertIn(str(c.PERMIT),missing.stderr)
        self.assertNotIn('PermissionError',missing.stderr)
        self.assertEqual(before,f.reader.capture_tree(c.ROOT))

    def test_real_installed_main_execution_verifier_with_bound_permit(self):
        f=self.fixture(); before=f.reader.capture_tree(c.ROOT)
        result=self.run_uid1000(f,'verify-execution')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(before,f.reader.capture_tree(c.ROOT))

    def test_root_only_each_content_drift_real_uid1000(self):
        for name in c.ROOT_ONLY_NAMES:
            with self.subTest(name=name):
                f=Fixture()
                try:
                    p=c.ROOT/'manifests'/name
                    write(p,b'changed root-only evidence\n',0o600,0,0)
                    before=f.reader.capture_tree(c.ROOT)
                    result=self.run_uid1000(f,'verify-ready')
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn('root-only historical metadata drift',result.stderr)
                    self.assertEqual(before,f.reader.capture_tree(c.ROOT))
                finally:f.close()

    def test_fixed_root_only_permission_link_and_inode_drift(self):
        for mode in ('permission','symlink','hardlink','new_inode'):
            with self.subTest(mode=mode):
                f=Fixture()
                try:
                    p=c.ROOT/'manifests'/c.ROOT_ONLY_NAMES[0]
                    if mode=='permission':os.chmod(p,0o640)
                    elif mode=='symlink':p.unlink();p.symlink_to(c.FACT)
                    elif mode=='hardlink':os.link(p,f.base/'extra-hardlink')
                    else:
                        payload=p.read_bytes();p.unlink();write(p,payload,0o600,0,0)
                    result=self.run_uid1000(f,'verify-ready')
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn('root-only historical metadata drift',result.stderr)
                finally:f.close()

    def test_unknown_unreadable_object_is_not_silently_ignored(self):
        f=self.fixture(); p=c.ROOT/'manifests/not-in-fixed-eight.json'
        write(p,b'unknown root-only\n',0o600,0,0)
        result=self.run_uid1000(f,'verify-ready')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('PermissionError',result.stderr)
        self.assertIn(str(p),result.stderr)

    def test_root_history_verification_does_not_use_metadata_substitution(self):
        f=self.fixture(); original_capture=f.reader.capture_tree; seen=[]
        def root_capture(path):
            seen.append(path)
            # Isolate only the unrelated real /root location from a fixture.
            return {} if str(path)=='/root/deeph-m9-control' else original_capture(path)
        with mock.patch.object(f.reader,'capture_tree',side_effect=root_capture), \
             mock.patch.object(c,'root_only_metadata',side_effect=AssertionError('root substituted content')):
            c.runtime_and_history(f.reader,f.baseline,True,True)
        self.assertIn(c.ROOT/'manifests',seen)
        self.assertIn(Path('/root/deeph-m9-control'),seen)

    def test_history_attestation_change_rejected_by_real_uid(self):
        f=self.fixture(); jwrite(c.GATE,dict(f.gate,history_attestation_sha256='0'*64),0o640)
        result=self.run_uid1000(f,'verify-ready')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('root history attestation binding differs',result.stderr)

    def test_v1_gate_and_old_operation_are_not_v2_authority(self):
        f=self.fixture(); old=dict(f.gate,schema='m9-source-build-readiness-v1',
            operation_id='72cefbe283654fd5b85fb2e66d9c2dfb')
        jwrite(c.GATE,old,0o640)
        result=self.run_uid1000(f,'verify-ready')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('build gate scope/field mismatch',result.stderr)


if __name__ == '__main__':
    unittest.main()
