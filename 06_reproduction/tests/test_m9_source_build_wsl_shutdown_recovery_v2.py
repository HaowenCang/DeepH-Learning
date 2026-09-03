"""Isolated tests for the WSL-shutdown recovery. No formal recovery is called."""
import base64
import gzip
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from contextlib import contextmanager
from unittest import mock

PROJECT=Path('/mnt/e/Projects/Codex/DeepH')
SOURCE=PROJECT/'06_reproduction/controllers/m9_source_build_wsl_shutdown_recovery_v2.py'
spec=importlib.util.spec_from_file_location('wsl_shutdown_recovery',SOURCE)
r=importlib.util.module_from_spec(spec)
exec(compile(SOURCE.read_bytes(),str(SOURCE),'exec',dont_inherit=True),r.__dict__)
helper=PROJECT/'06_reproduction/controllers/m9_py39_consumer_gate_completion.py'
reader=r.load_source('wsl_shutdown_recovery_receipts_fixture',helper,r.pinned(helper,r.RECEIPTS_SHA))


def runtime_raw():
    state={'active_overlap_transaction':r.FAILURE_ID,'hard_stopped':False,
        'cpu_seconds':{'overlap_build':7507.245045788001,'overlap_smoke':0.0,'overlap_batch':0.0},
        'gpu_seconds':{'compatibility':54.84820560599999,'training':0.0,'physical_validation':0.0},
        'cpu_adjustments':[{'credited_seconds':7200.075310528}],'last_event_utc':'old','keep':'state'}
    workflow={'active_transaction':r.FAILURE_ID,'hard_stopped':False,'stage':'SOURCES_PREPARED','keep':'workflow'}
    tx={'schema_version':'m9-overlap-transaction-v1','transaction_id':r.FAILURE_ID,'state':'RUNNING',
        'action':'source_build','bucket':'overlap_build','child_pid':397,
        'start_utc':'2026-09-01T14:46:52.111163Z','keep':'transaction'}
    return {r.STATE:r.encode(state),r.WORKFLOW:r.encode(workflow),r.TX:r.encode(tx),
            r.LEDGER:b'{"event":"OLD"}\n'}


def add_process(pid,argv,cwd,exe):
    process=r.PROC/str(pid); process.mkdir()
    (process/'cmdline').write_bytes(b'\0'.join(os.fsencode(value) for value in argv)+b'\0')
    (process/'cwd').symlink_to(cwd,target_is_directory=True)
    (process/'exe').symlink_to(exe)
    return process


class FixtureBudget:
    def __init__(self):
        self.reject=False

    def violations(self,_state,_forecast):
        return ['injected_storage_drift'] if self.reject else []

    def storage_snapshot(self,_state):
        return {'fixture_storage_bytes':1}


class Fixture:
    def __enter__(self):
        self.temp=tempfile.TemporaryDirectory(prefix='m9-wsl-shutdown-recovery-test-')
        root=Path(self.temp.name); self.root=root
        overrides={'ROOT':root/'runtime','PRIVATE':root/'private/recovery','PROC':root/'proc',
            'CONTROL_UID':os.geteuid(),'CONTROL_GID':os.getegid(),'SNAPSHOT_GID':os.getegid()}
        overrides.update({'LOCK':overrides['ROOT']/'manifests/budget.lock',
            'STATE':overrides['ROOT']/'manifests/budget_state.json',
            'WORKFLOW':overrides['ROOT']/'manifests/overlap_workflow_state.json',
            'TX':overrides['ROOT']/'manifests/overlap_transaction.json',
            'LEDGER':overrides['ROOT']/'manifests/budget_ledger.jsonl',
            'CAPABILITY':overrides['ROOT']/'manifests/overlap_capabilities/c.consumed.json',
            'RECEIPT':overrides['ROOT']/'manifests/overlap_capabilities/c.launcher-receipt.json',
            'PERMIT':overrides['ROOT']/'manifests/permit.json',
            'GATE':overrides['ROOT']/'manifests/gate.json',
            'BUILD':overrides['ROOT']/'software/build','CLEAN':overrides['ROOT']/'software/clean',
            'PRIOR_ARCHIVE':overrides['ROOT']/'software/prior-archive',
            'PRIOR_LOG_ARCHIVE':overrides['ROOT']/'logs/prior-log-archive',
            'LOGS':overrides['ROOT']/'logs/build','SNAPSHOT':overrides['ROOT']/'controls/recovery'})
        overrides.update({'ARCHIVE':overrides['BUILD'].with_name('archive'),
            'LOG_ARCHIVE':overrides['LOGS'].with_name('log-archive'),
            'STAGING':overrides['BUILD'].with_name('staging'),
            'JOURNAL':overrides['PRIVATE']/'journal.json'})
        self.patch=mock.patch.multiple(r,**overrides); self.patch.start()
        for path in (r.ROOT/'manifests/overlap_capabilities',r.ROOT/'controls',r.ROOT/'software',
                     r.ROOT/'logs',r.PRIVATE.parent,r.PROC): path.mkdir(parents=True,exist_ok=True)
        self.raw=runtime_raw()
        # runtime_raw was created after patching and therefore uses fixture paths.
        for path,data in self.raw.items(): path.write_bytes(data); os.chmod(path,0o644)
        r.LOCK.write_bytes(b''); os.chmod(r.LOCK,0o644)
        r.BUILD.mkdir(); (r.BUILD/'source.txt').write_text('interrupted',encoding='utf-8')
        (r.BUILD/'object.o').write_bytes(b'partial')
        r.CLEAN.mkdir(); (r.CLEAN/'source.txt').write_text('clean',encoding='utf-8')
        (r.CLEAN/'nested').mkdir(); (r.CLEAN/'nested/input').write_bytes(b'frozen')
        (r.CLEAN/'nested/link').symlink_to('input')
        r.PRIOR_ARCHIVE.mkdir(); (r.PRIOR_ARCHIVE/'prior.txt').write_text('prior',encoding='utf-8')
        r.PRIOR_LOG_ARCHIVE.mkdir(); (r.PRIOR_LOG_ARCHIVE/'prior.log').write_text('prior\n',encoding='utf-8')
        r.LOGS.mkdir(); (r.LOGS/'hdf5-check.log').write_text('Terminated\n',encoding='utf-8')
        self.capability={'state':'CONSUMED','capability_id':r.CAPABILITY_ID,
            'budget_argv':['python','formal-parent'],'launcher_argv':['python','formal-child']}
        r.CAPABILITY.write_bytes(r.encode(self.capability))
        r.GATE.write_bytes(b'fixture gate\n')
        r.PERMIT.write_bytes(b'fixture permit\n')
        initial=r.formal_namespace(reader)
        for index in range(275-len(initial)):
            (r.ROOT/'controls'/('padding-%03d' % index)).write_bytes(b'fixture\n')
        self.expected=r.formal_namespace(reader)
        if len(self.expected)!=275: raise AssertionError('fixture formal namespace must contain 275 objects')
        formal_raw=json.dumps(self.expected,ensure_ascii=False,sort_keys=True,
                              separators=(',',':')).encode('utf-8')
        products={str(r.ROOT/'env/forbidden-product'):False}
        build=reader.capture_tree(r.BUILD); logs=reader.capture_tree(r.LOGS)
        prior=reader.capture_tree(r.PRIOR_ARCHIVE); prior_logs=reader.capture_tree(r.PRIOR_LOG_ARCHIVE)
        self.evidence={'schema':'m9-source-build-v4-interruption-postexecution-evidence-v1',
            'classification':{'verdict':'FAIL','blocking':1,'non_blocking':0,
                'blocking_id':'M9-SB-V4-INT-B01','external_wsl_instance_interruption_nonterminal':True,
                'ordinary_budget_failure_committed':False,'windows_full_shutdown_is_same_event':False},
            'formal_namespace':{'count':len(self.expected),'canonical_json_bytes':len(formal_raw),
                'canonical_sha256':r.sha(formal_raw),
                'canonical_json_gzip_base64':base64.b64encode(gzip.compress(formal_raw)).decode('ascii')},
            'timeline':{'conservative_wall_upper_bound_seconds':r.ELAPSED,
                'upper_bound_end_utc':r.SHUTDOWN_UTC},
            'runtime_raw':{str(path):{'gzip_base64':base64.b64encode(gzip.compress(data)).decode('ascii'),
                'bytes':len(data),'sha256':r.sha(data)} for path,data in self.raw.items()},
            'capability':{'content':self.capability,
                'consumed_receipt':reader.filesystem_receipt(r.CAPABILITY),
                'bound_path_absent':True,'launcher_receipt_absent':True},
            'authority':{'v4_gate_sha256':r.sha(r.GATE.read_bytes()),
                'v4_permit_sha256':r.sha(r.PERMIT.read_bytes()),
                'preexecution_evidence_sha256':r.sha(b'preexecution evidence')},
            'trees':{'build':{'count':len(build),'canonical_sha256':r.canonical(build)},
                'retired_clean':{'count':len(reader.capture_tree(r.CLEAN)),
                    'canonical_sha256':r.canonical(reader.capture_tree(r.CLEAN))},
                'prior_interrupted_archive':{'count':len(prior),'canonical_sha256':r.canonical(prior)},
                'prior_log_archive':{'count':len(prior_logs),'canonical_sha256':r.canonical(prior_logs)},
                'current_logs':{'count':len(logs),'canonical_sha256':r.canonical(logs),
                    'raw_files':{str(path):{'bytes':path.stat().st_size,
                        'sha256':r.sha(path.read_bytes())} for path in r.LOGS.iterdir()}}},
            'products':{'expected_final_products_present':products,
                'hdf5_partial_intermediates_present':True,'openmx_compile_started':False},
            'processes':{'matched_build_processes':[]},
            'recovery_acceptance':{'must_charge_controller_compatible_wall_upper_bound_seconds':r.ELAPSED,
                'must_bind_build_tree_sha256':r.canonical(build),'must_bind_current_logs_sha256':r.canonical(logs),
                'must_bind_complete_275_formal_namespace_sha256':r.sha(formal_raw),
                'must_preserve_consumed_capability_sha256':r.sha(r.CAPABILITY.read_bytes())}}
        self.payloads={r.SELF:b'controller',r.INTERRUPTION_EVIDENCE:r.encode(self.evidence),
            r.INTERRUPTION_REPORT:b'report',r.AUTH:b'authorization',r.FROZEN:b'frozen',
            r.PREEXECUTION_EVIDENCE:b'preexecution evidence',r.V4_MANIFEST:b'v4 manifest',
            r.BUDGET:b'budget module',
            r.REPORT:b'implementation report',r.VERDICT:b'verdict'}
        self.target,self.event,self.line=r.targets(self.raw,self.payloads)
        self.budget=FixtureBudget()
        return self

    def __exit__(self,*_):
        self.patch.stop(); self.temp.cleanup()


@contextmanager
def fixture_authority(f):
    original=r.pinned
    def fixture_pinned(path,expected=None):
        if path in f.payloads:
            data=f.payloads[path]
            if expected is not None and r.sha(data)!=expected:
                raise ValueError('fixture digest differs')
            return data
        return original(path,expected)
    interrupted=r.canonical(reader.capture_tree(r.BUILD))
    clean=r.canonical(reader.capture_tree(r.CLEAN))
    with mock.patch.object(r,'pinned',side_effect=fixture_pinned), \
            mock.patch.multiple(r,EXPECTED_INTERRUPTED_TREE=interrupted,EXPECTED_CLEAN_TREE=clean,
                EXPECTED_LOG_TREE=r.canonical(reader.capture_tree(r.LOGS)),
                EXPECTED_PRIOR_ARCHIVE=r.canonical(reader.capture_tree(r.PRIOR_ARCHIVE)),
                EXPECTED_PRIOR_LOG_ARCHIVE=r.canonical(reader.capture_tree(r.PRIOR_LOG_ARCHIVE)),
                EXPECTED_GATE_SHA=r.sha(r.GATE.read_bytes()),EXPECTED_PERMIT_SHA=r.sha(r.PERMIT.read_bytes()),
                EXPECTED_BUILD_COUNT=len(reader.capture_tree(r.BUILD)),
                EXPECTED_CLEAN_COUNT=len(reader.capture_tree(r.CLEAN)),
                EXPECTED_PRIOR_ARCHIVE_COUNT=len(reader.capture_tree(r.PRIOR_ARCHIVE)),
                EXPECTED_LOG_COUNT=len(reader.capture_tree(r.LOGS)),
                PREEXECUTION_EVIDENCE_SHA=r.sha(b'preexecution evidence')):
        yield


class RecoveryTests(unittest.TestCase):
    def test_real_frozen_authority_closure_with_strict_fixture_verdict(self):
        with tempfile.TemporaryDirectory(prefix='m9-wsl-shutdown-authority-') as directory:
            root=Path(directory); report=root/'implementation.md'; verdict=root/'verdict.json'
            report.write_text('independent fixture only\n',encoding='utf-8')
            frozen_raw=r.FROZEN.read_bytes(); frozen_sha=r.sha(frozen_raw); report_sha=r.sha(report.read_bytes())
            value={'schema':'m9-wsl-shutdown-recovery-implementation-verdict-v2','status':'PASS',
                'blocking':0,'non_blocking':0,'frozen_sha256':frozen_sha,
                'report_path':str(report),'report_sha256':report_sha}
            verdict.write_bytes(r.encode(value))
            calls=[]; original=r.pinned
            def traced(path,expected=None):
                calls.append(Path(path)); return original(path,expected)
            with mock.patch.multiple(r,REPORT=report,VERDICT=verdict), \
                    mock.patch.object(r,'pinned',side_effect=traced):
                action,payloads,actual_reader,budget=r.authority([
                    r.sha(r.SELF.read_bytes()),'preflight',frozen_sha,r.sha(verdict.read_bytes()),report_sha])
            self.assertEqual(action,'preflight'); self.assertIsNotNone(actual_reader); self.assertTrue(hasattr(budget,'violations'))
            self.assertEqual(payloads[r.FROZEN],frozen_raw)
            direct={Path(name) for name in json.loads(r.V4_MANIFEST.read_bytes())['files']}
            expected=set(r.SOURCE_SET)|{r.FROZEN,report,verdict}|direct
            self.assertEqual(set(calls),expected)
            self.assertEqual(payloads[r.BUDGET],r.BUDGET.read_bytes())
            self.assertEqual(payloads[r.RECEIPTS],r.RECEIPTS.read_bytes())

    def test_v4_authority_pins_exact_direct_members_not_historical_mutable_leaves(self):
        with tempfile.TemporaryDirectory(prefix='m9-direct-authority-') as directory:
            root=Path(directory); leaf=root/'historical-leaf'; history=root/'history.json'
            leaf.write_bytes(b'current bytes differ from historical declaration')
            history_raw=r.encode({'schema':'history','files':{str(leaf):'0'*64}})
            history.write_bytes(history_raw)
            v4=r.encode({'schema':'m9-source-build-frozen-v4',
                         'files':{str(history):r.sha(history_raw)}})
            calls=[]; original=r.pinned
            def traced(path,expected=None):
                calls.append(Path(path)); return original(path,expected)
            with mock.patch.object(r,'pinned',side_effect=traced), \
                    mock.patch.object(r,'EXPECTED_V4_DIRECT_MEMBERS',1):
                result=r.validate_v4_direct_authority(v4)
            self.assertEqual(result,{str(history):r.sha(history_raw)})
            self.assertEqual(calls,[history])
            self.assertNotIn(leaf,calls)

    def test_formal_namespace_roots_are_fully_fixture_local(self):
        with Fixture() as f:
            for path in r.formal_roots():
                self.assertTrue(r.is_beneath(path,f.root))

    def test_targets_preserve_history_and_charge_conservative_upper_bound(self):
        with Fixture() as f:
            state=json.loads(f.target[r.STATE]); workflow=json.loads(f.target[r.WORKFLOW]); tx=json.loads(f.target[r.TX])
            self.assertAlmostEqual(state['cpu_seconds']['overlap_build'],7645.646848354001,places=10)
            self.assertEqual(state['gpu_seconds'],json.loads(f.raw[r.STATE])['gpu_seconds'])
            self.assertIsNone(state['active_overlap_transaction']); self.assertFalse(state['hard_stopped'])
            self.assertEqual(workflow['stage'],'SOURCES_PREPARED'); self.assertIsNone(workflow['active_transaction'])
            self.assertEqual(tx['state'],'FAILED_COMMITTED'); self.assertIsNone(tx['exit_code'])
            self.assertEqual(tx['reasons'],['wsl_shutdown_external_interruption'])
            self.assertEqual(tx['elapsed_semantics'],'conservative_wall_upper_bound_not_measured_cpu')
            self.assertFalse(f.event['source_build_authorized'])
            self.assertEqual(f.target[r.LEDGER],f.raw[r.LEDGER]+f.line)

    def test_invalid_orphan_semantics_are_rejected(self):
        variants=[('transaction_id','other'),('state','SUCCESS_COMMITTED'),('action','smoke_run'),
                  ('child_pid',396),('start_utc','other')]
        for field,value in variants:
            with self.subTest(field=field),Fixture() as f:
                raw=dict(f.raw); tx=json.loads(raw[r.TX]); tx[field]=value; raw[r.TX]=r.encode(tx)
                with self.assertRaisesRegex(ValueError,'orphaned transaction semantics'):
                    r.targets(raw,f.payloads)

    def test_portable_clone_matches_clean_without_hardlinks(self):
        with Fixture() as f:
            wanted=r.portable_tree(r.CLEAN,reader)
            r.clone_tree(r.CLEAN,r.STAGING)
            self.assertEqual(r.portable_tree(r.STAGING,reader),wanted)
            src=(r.CLEAN/'source.txt').stat(); dst=(r.STAGING/'source.txt').stat()
            self.assertNotEqual((src.st_dev,src.st_ino),(dst.st_dev,dst.st_ino))
            (r.STAGING/'source.txt').write_text('changed',encoding='utf-8')
            self.assertEqual((r.CLEAN/'source.txt').read_text(encoding='utf-8'),'clean')

    def test_commit_archives_partial_tree_and_rebuilds_clean_tree(self):
        with Fixture() as f:
            clean=r.portable_tree(r.CLEAN,reader); old_ledger=f.raw[r.LEDGER]
            with fixture_authority(f):
                seal=r.verify_current(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw)
                result=r.commit(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw,
                                f.target,f.event,f.line,seal)
            self.assertEqual(result['status'],'RECOVERY_SUCCESS_COMMITTED')
            self.assertTrue(r.ARCHIVE.is_dir()); self.assertTrue((r.ARCHIVE/'object.o').is_file())
            self.assertTrue(r.LOG_ARCHIVE.is_dir()); self.assertEqual(r.portable_tree(r.BUILD,reader),clean)
            self.assertEqual(r.LEDGER.read_bytes(),old_ledger+f.line)
            self.assertEqual([x['phase'] for x in json.loads(r.JOURNAL.read_bytes())['history']],list(r.PHASES))
            self.assertFalse(result['source_build_authorized'])

    def test_nonformal_drift_between_validation_and_first_write_is_zero_write_rejected(self):
        variants=('namespace','build','clean','prior_archive','prior_log_archive',
                  'gate','permit','log','product','process','storage')
        for variant in variants:
            with self.subTest(variant=variant),Fixture() as f,fixture_authority(f):
                seal=r.verify_current(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw)
                process_patch=mock.patch.object(r,'process_alive',return_value=False)
                if variant=='namespace': (r.ROOT/'manifests/unknown-object').write_bytes(b'unknown')
                elif variant=='build': (r.BUILD/'source.txt').write_text('drift',encoding='utf-8')
                elif variant=='clean': (r.CLEAN/'source.txt').write_text('drift',encoding='utf-8')
                elif variant=='prior_archive': (r.PRIOR_ARCHIVE/'prior.txt').write_text('drift',encoding='utf-8')
                elif variant=='prior_log_archive': (r.PRIOR_LOG_ARCHIVE/'prior.log').write_text('drift\n',encoding='utf-8')
                elif variant=='gate': r.GATE.write_bytes(b'drift gate\n')
                elif variant=='permit': r.PERMIT.write_bytes(b'drift permit\n')
                elif variant=='log': (r.LOGS/'hdf5-check.log').write_text('drift\n',encoding='utf-8')
                elif variant=='product':
                    product=Path(next(iter(f.evidence['products']['expected_final_products_present'])))
                    product.parent.mkdir(parents=True,exist_ok=True); product.write_bytes(b'appeared')
                elif variant=='process': process_patch=mock.patch.object(r,'process_alive',return_value=True)
                elif variant=='storage': f.budget.reject=True
                before=reader.capture_tree(f.root)
                with process_patch:
                    with self.assertRaisesRegex(ValueError,'drift before first write'):
                        r.commit(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw,
                                 f.target,f.event,f.line,seal)
                self.assertEqual(reader.capture_tree(f.root),before)
                self.assertFalse(r.PRIVATE.exists())
                self.assertFalse(r.ARCHIVE.exists())
                self.assertEqual(r.LEDGER.read_bytes(),f.raw[r.LEDGER])

    def test_orphan_make_appearing_after_seal_is_zero_write_rejected(self):
        with Fixture() as f,fixture_authority(f):
            seal=r.verify_current(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw)
            add_process(901,['/usr/bin/make','-j2'],r.BUILD,'/usr/bin/make')
            before=reader.capture_tree(f.root)
            with self.assertRaisesRegex(ValueError,'drift before first write'):
                r.commit(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw,
                         f.target,f.event,f.line,seal)
            self.assertEqual(reader.capture_tree(f.root),before)
            self.assertFalse(r.PRIVATE.exists())

    def test_validate_preflight_is_a_full_zero_write_double_check(self):
        with Fixture() as f,fixture_authority(f):
            before=reader.capture_tree(f.root)
            result=r.validate('preflight',f.payloads,reader,f.budget)
            after=reader.capture_tree(f.root)
            self.assertEqual(result['status'],'PREFLIGHT_PASS')
            self.assertEqual(result['writes'],0)
            self.assertEqual(after,before)

    def test_each_persistence_window_preserves_evidence_and_is_not_replayable(self):
        for phase in r.PHASES:
            with self.subTest(phase=phase),Fixture() as f,fixture_authority(f):
                seal=r.verify_current(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw)
                original=r.checkpoint
                def inject(journal,current):
                    original(journal,current)
                    if current==phase: raise OSError('injected after '+phase)
                with mock.patch.object(r,'checkpoint',side_effect=inject):
                    with self.assertRaisesRegex(OSError,'injected after'):
                        r.commit(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw,
                                 f.target,f.event,f.line,seal)
                self.assertTrue(r.PRIVATE.is_dir())
                self.assertTrue(r.JOURNAL.is_file())
                completed=r.PHASES.index(phase)
                if completed>=1: self.assertTrue(r.ARCHIVE.is_dir())
                if completed>=2: self.assertTrue(r.LOG_ARCHIVE.is_dir())
                if completed>=3: self.assertEqual(r.portable_tree(r.BUILD,reader),
                                                   seal['clean_portable'])
                if completed>=4: self.assertEqual(r.LEDGER.read_bytes(),f.raw[r.LEDGER]+f.line)
                if completed>=8: self.assertTrue(r.SNAPSHOT.is_dir())
                with self.assertRaisesRegex(ValueError,'drift before first write'):
                    r.commit(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw,
                             f.target,f.event,f.line,seal)

    def test_clone_fsyncs_every_regular_file_and_nested_directory(self):
        with Fixture() as f:
            synced=[]; original=r.os.fsync
            def record(fd):
                mode=os.fstat(fd).st_mode
                synced.append('directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else 'other')
                return original(fd)
            with mock.patch.object(r.os,'fsync',side_effect=record): r.clone_tree(r.CLEAN,r.STAGING)
            file_count=sum(1 for p in r.STAGING.rglob('*') if p.is_file() and not p.is_symlink())
            directory_count=1+sum(1 for p in r.STAGING.rglob('*') if p.is_dir() and not p.is_symlink())
            self.assertGreaterEqual(synced.count('file'),file_count)
            self.assertGreaterEqual(synced.count('directory'),directory_count)

    def test_clone_fsync_faults_stop_before_install_and_preserve_staging(self):
        for target in ('file','nested_directory'):
            with self.subTest(target=target),Fixture() as f:
                original=r.os.fsync; injected=[False]
                def fail(fd):
                    mode=os.fstat(fd).st_mode
                    linked=os.readlink('/proc/self/fd/'+str(fd))
                    selected=(target=='file' and stat.S_ISREG(mode) or
                              target=='nested_directory' and stat.S_ISDIR(mode)
                              and linked.endswith('/nested'))
                    if selected and not injected[0]:
                        injected[0]=True
                        raise OSError('injected clone fsync fault')
                    return original(fd)
                with mock.patch.object(r.os,'fsync',side_effect=fail):
                    with self.assertRaisesRegex(OSError,'clone fsync fault'):
                        r.clone_tree(r.CLEAN,r.STAGING)
                self.assertTrue(injected[0])
                self.assertTrue(r.STAGING.exists())
                self.assertEqual((r.BUILD/'source.txt').read_text(encoding='utf-8'),'interrupted')
                self.assertFalse(r.ARCHIVE.exists())

    def test_clone_drift_is_rejected_before_install_and_cannot_be_replayed(self):
        with Fixture() as f,fixture_authority(f):
            seal=r.verify_current(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw)
            original=r.clone_tree
            def drift(source,destination):
                original(source,destination)
                (destination/'source.txt').write_text('post-copy drift',encoding='utf-8')
            with mock.patch.object(r,'clone_tree',side_effect=drift):
                with self.assertRaisesRegex(ValueError,'clean clone differs'):
                    r.commit(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw,
                             f.target,f.event,f.line,seal)
            self.assertTrue(r.ARCHIVE.is_dir())
            self.assertTrue(r.LOG_ARCHIVE.is_dir())
            self.assertTrue(r.STAGING.is_dir())
            self.assertFalse(r.BUILD.exists())
            self.assertEqual(r.LEDGER.read_bytes(),f.raw[r.LEDGER])
            with self.assertRaisesRegex(ValueError,'drift before first write'):
                r.commit(f.payloads,reader,f.budget,f.evidence,f.expected,f.raw,
                         f.target,f.event,f.line,seal)

    def test_any_preexisting_recovery_target_rejects_without_changes(self):
        for name in ('archive','log_archive','staging','private','snapshot'):
            with self.subTest(name=name),Fixture() as f:
                path={'archive':r.ARCHIVE,'log_archive':r.LOG_ARCHIVE,'staging':r.STAGING,
                      'private':r.PRIVATE,'snapshot':r.SNAPSHOT}[name]
                path.mkdir(parents=True)
                before=f.raw[r.LEDGER]
                with self.assertRaisesRegex(ValueError,'non-pristine'): r.require_pristine()
                self.assertEqual(r.LEDGER.read_bytes(),before)

    def test_short_runtime_write_is_not_silently_lost(self):
        with Fixture() as f:
            original=os.write
            with mock.patch.object(r.os,'write',side_effect=lambda fd,data: original(fd,data[:max(1,len(data)//3)])):
                r.write_file(r.STATE,f.target[r.STATE],replace=True)
            self.assertEqual(r.STATE.read_bytes(),f.target[r.STATE])

    def test_zero_write_fails_and_preserves_target(self):
        with Fixture() as f:
            before=r.STATE.read_bytes()
            with mock.patch.object(r.os,'write',return_value=0):
                with self.assertRaisesRegex(OSError,'short recovery write'):
                    r.write_file(r.STATE,f.target[r.STATE],replace=True)
            self.assertEqual(r.STATE.read_bytes(),before)
            self.assertTrue(r.STATE.with_name(r.STATE.name+'.wsl-shutdown-recovery-v2.tmp').exists())

    def test_partial_ledger_append_is_preserved_and_not_replayed(self):
        with Fixture() as f:
            original=os.write; calls=[0]
            def partial(fd,data):
                calls[0]+=1
                if calls[0]>1: raise OSError('injected partial event')
                return original(fd,data[:11])
            with mock.patch.object(r.os,'write',side_effect=partial):
                with self.assertRaisesRegex(OSError,'partial event'): r.append_ledger(f.raw[r.LEDGER],f.line)
            self.assertEqual(r.LEDGER.read_bytes(),f.raw[r.LEDGER]+f.line[:11])
            with self.assertRaisesRegex(ValueError,'ledger prefix differs'):
                r.append_ledger(f.raw[r.LEDGER],f.line)

    def test_phase_order_and_replay_are_rejected(self):
        with Fixture() as f:
            r.PRIVATE.mkdir(); r.JOURNAL.parent.mkdir(parents=True,exist_ok=True)
            journal={'history':[]}
            with self.assertRaisesRegex(ValueError,'phase order'): r.checkpoint(journal,'SUCCESS_COMMITTED')
        for action in ('resume','run','permit','build','install'):
            with self.subTest(action=action),self.assertRaisesRegex(ValueError,'no resume'):
                r.authority(['x',action,'x','x','x'])

    def test_process_detection_covers_wrapper_orphans_and_unrelated_processes(self):
        with Fixture() as f:
            self.assertFalse(r.process_alive(f.capability))
            add_process(101,['/usr/sbin/runuser','-u','user','--',*f.capability['budget_argv']],
                        f.root,'/usr/sbin/runuser')
            self.assertTrue(r.process_alive(f.capability))
        with Fixture() as f:
            add_process(102,['/usr/bin/make','-j2'],r.BUILD/'hdf5-source','/usr/bin/make')
            self.assertTrue(r.process_alive(f.capability))
        with Fixture() as f:
            add_process(103,['/usr/bin/gcc','-c','source.c'],r.BUILD/'openmx3.9','/usr/bin/gcc')
            self.assertTrue(r.process_alive(f.capability))
        with Fixture() as f:
            add_process(104,['/usr/bin/make','-j2'],f.root,'/usr/bin/make')
            self.assertFalse(r.process_alive(f.capability))

    def test_unreadable_process_identity_is_fail_closed(self):
        with Fixture() as f:
            process=add_process(105,['/usr/bin/make','-j2'],r.BUILD,'/usr/bin/make')
            original=Path.read_bytes
            def unreadable(path):
                if path==process/'cmdline': raise PermissionError('injected unreadable cmdline')
                return original(path)
            with mock.patch.object(Path,'read_bytes',new=unreadable):
                with self.assertRaisesRegex(ValueError,'cannot prove process unrelated'):
                    r.process_alive(f.capability)


if __name__=='__main__':
    unittest.main()
