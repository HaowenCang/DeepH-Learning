"""Root-only isolated recovery tests. No production write actions are called."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
SOURCE = PROJECT / '06_reproduction/controllers/m9_source_build_mpi_recovery_v1.py'
spec = importlib.util.spec_from_file_location('recovery', SOURCE)
r = importlib.util.module_from_spec(spec)
exec(compile(SOURCE.read_bytes(), str(SOURCE), 'exec', dont_inherit=True), r.__dict__)
helper_path = PROJECT / '06_reproduction/controllers/m9_py39_consumer_gate_completion.py'
reader = r.load_source('receipt_fixture', helper_path, r.pinned(helper_path, 'c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55'))


class Fixture:
    def __enter__(self):
        self.temp = tempfile.TemporaryDirectory(prefix='m9-mpi-recovery-test-')
        root = Path(self.temp.name)
        self.overrides = {'ROOT': root / 'runtime', 'PRIVATE': root / 'private/recovery'}
        self.overrides.update({'SNAPSHOT': self.overrides['ROOT'] / 'controls/repair',
            'JOURNAL': self.overrides['PRIVATE'] / 'journal.json'})
        for name, filename in [('LOCK','budget.lock'), ('STATE','budget_state.json'),
                               ('WORKFLOW','overlap_workflow_state.json'), ('LEDGER','budget_ledger.jsonl'),
                               ('TX','overlap_transaction.json')]:
            self.overrides[name] = self.overrides['ROOT'] / 'manifests' / filename
        self.patch = mock.patch.multiple(r, **self.overrides); self.patch.start()
        for path in (r.ROOT / 'controls', r.ROOT / 'manifests', r.PRIVATE.parent):
            path.mkdir(parents=True, mode=0o700)
        state = {'hard_stopped': True, 'active_overlap_transaction': None,
                 'cpu_seconds': {'overlap_build': 7214.469142588001, 'overlap_smoke': 0., 'overlap_batch': 0.},
                 'gpu_seconds': {'compatibility': 54.84820560599999, 'training': 0., 'physical_validation': 0.},
                 'cpu_adjustments': [{'credited_seconds': 7200.075310528}],
                 'history': {'keep': ['all', 'unchanged']}, 'last_event_utc': 'old'}
        workflow = {'hard_stopped': True, 'stage': 'HARD_STOP', 'active_transaction': None,
                    'hard_stop_reason': ['overlap_command_failed'], 'hard_stop_utc': 'old', 'history': 2}
        tx = {'state': 'FAILED_COMMITTED', 'transaction_id': r.FAILURE_ID, 'action': 'source_build',
              'reasons': ['overlap_command_failed'], 'timed_out': False, 'exit_code': 1}
        self.raw = {r.STATE: r.encode(state), r.WORKFLOW: r.encode(workflow), r.TX: r.encode(tx),
                    r.LEDGER: b'{"event":"HISTORICAL_FAILURE"}\n'}
        for path, data in self.raw.items():
            path.write_bytes(data); os.chown(path, 1000, 1000); os.chmod(path, 0o644)
        r.LOCK.write_bytes(b''); os.chown(r.LOCK, 1000, 1000); os.chmod(r.LOCK, 0o644)
        self.fd = os.open(r.LOCK, os.O_RDWR)
        self.before = r.capture(reader)
        self.guard = r.Guard(reader, self.before, self.fd)
        self.target, self.event, self.line = r.targets(self.raw, 'fixed-utc', {'test': 'only'})
        self.journal = {'history': [], 'target_sha256': {str(p):r.sha(b) for p,b in self.target.items()},
                        'event': self.event, 'source_build_authorized': False}
        self.c = mock.Mock()
        self.tool = mock.patch.object(r, 'real_toolchain', return_value={'returncode':0, 'build_executed':False})
        self.tool.start()
        return self

    def commit(self):
        return r.commit_recovery(self.guard, {Path('/fixture/input-' + str(i)): b'authority' for i in range(12)},
            self.raw, self.target, self.line, {name: b'not executable' for name in ('adapter.py','original.py','common.py','contract.json')}, b'{}\n',
            self.journal, self.c, time.monotonic())

    def __exit__(self, *_):
        self.tool.stop(); os.close(self.fd); self.patch.stop(); self.temp.cleanup()


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(os.geteuid(), 0, 'fixture security tests require root')

    def test_exact_target_whitelist_preserves_budget_and_history(self):
        with Fixture() as f:
            state, workflow = (json.loads(f.target[p]) for p in (r.STATE, r.WORKFLOW))
            old_state, old_workflow = (json.loads(f.raw[p]) for p in (r.STATE, r.WORKFLOW))
            state['hard_stopped'] = True; state['last_event_utc'] = old_state['last_event_utc']
            del state['recovered_from_source_build_mpi_failure']
            workflow['hard_stopped'] = True; workflow['stage'] = 'HARD_STOP'
            del workflow['recovered_from_source_build_mpi_failure']
            self.assertEqual(state, old_state); self.assertEqual(workflow, old_workflow)
            self.assertFalse(f.event['source_build_authorized'])

    def test_success_exact_runtime_and_failed_tx_identity_preserved(self):
        with Fixture() as f:
            result = f.commit()
            self.assertEqual(result['status'], 'RECOVERY_SUCCESS_COMMITTED')
            for path, data in f.target.items():
                self.assertEqual(path.read_bytes(), data)
            self.assertEqual(reader.filesystem_receipt(r.TX), f.before[str(r.TX)])
            journal = json.loads(r.JOURNAL.read_bytes())
            self.assertEqual([x['phase'] for x in journal['history']], list(r.PHASES))
            for entry in journal['history']:
                self.assertEqual(entry['post_runtime_receipts'][str(r.TX)], f.before[str(r.TX)])
            before = r.capture(reader)
            with self.assertRaisesRegex(ValueError, 'non-pristine'):
                r.require_pristine()
            self.assertEqual(r.capture(reader), before)

    def test_any_preexisting_target_or_tmp_rejected(self):
        for name in ('private', 'snapshot', 'staging', 'state_tmp', 'workflow_tmp'):
            with self.subTest(name=name), Fixture() as f:
                path = {'private':r.PRIVATE, 'snapshot':r.SNAPSHOT,
                        'staging':r.SNAPSHOT.with_name(r.SNAPSHOT.name+'.staging'),
                        'state_tmp':r.STATE.with_name(r.STATE.name+'.mpi-recovery.tmp'),
                        'workflow_tmp':r.WORKFLOW.with_name(r.WORKFLOW.name+'.mpi-recovery.tmp')}[name]
                path.write_bytes(b'preserve')
                with self.assertRaisesRegex(ValueError, 'non-pristine'):
                    r.require_pristine()
                self.assertEqual(path.read_bytes(), b'preserve')

    def test_identical_bytes_new_inode_rejected(self):
        with Fixture() as f:
            old = r.STATE.with_name('saved')
            r.STATE.rename(old); r.STATE.write_bytes(f.raw[r.STATE])
            with self.assertRaisesRegex(ValueError, 'namespace/identity drift'):
                f.guard.check()

    def test_lock_replaced_same_bytes_rejected(self):
        with Fixture() as f:
            r.LOCK.rename(r.LOCK.with_name('saved-lock')); r.LOCK.write_bytes(b'')
            with self.assertRaisesRegex(ValueError, 'lock path identity drift'):
                f.guard.check()

    def test_extra_object_and_ledger_unknown_tail_rejected(self):
        for variant in ('extra', 'tail'):
            with self.subTest(variant=variant), Fixture() as f:
                if variant == 'extra':
                    (r.PRIVATE.parent / 'unexpected').write_bytes(b'x')
                else:
                    with r.LEDGER.open('ab') as stream: stream.write(b'unknown')
                with self.assertRaisesRegex(ValueError, 'namespace/identity drift'):
                    f.guard.append(r.LEDGER, f.raw[r.LEDGER], f.line)

    def test_phase_order_rejected_before_write(self):
        with Fixture() as f:
            with self.assertRaisesRegex(ValueError, 'phase order'):
                r.checkpoint(f.guard, f.journal, 'SUCCESS_COMMITTED')
            self.assertEqual(r.capture(reader), f.before)

    def test_short_writes_are_completed_not_silently_lost(self):
        with Fixture() as f:
            original = os.write
            with mock.patch.object(r.os, 'write', side_effect=lambda fd, data: original(fd, data[:max(1,len(data)//3)])):
                f.commit()
            self.assertEqual(r.LEDGER.read_bytes(), f.target[r.LEDGER])

    def test_zero_write_preserves_partial_evidence_and_rejects_replay(self):
        with Fixture() as f:
            with mock.patch.object(r.os, 'write', return_value=0):
                with self.assertRaisesRegex(OSError, 'short recovery write'):
                    f.commit()
            self.assertTrue(r.PRIVATE.exists())
            self.assertTrue(json.loads(r.STATE.read_bytes())['hard_stopped'])
            self.assertEqual(r.LEDGER.read_bytes(), f.raw[r.LEDGER])
            with self.assertRaisesRegex(ValueError, 'non-pristine'):
                r.require_pristine()

    def test_failure_after_every_durable_file_window_never_replays(self):
        with Fixture() as f:
            calls = []
            original = f.guard.file
            def count(*a, **kw):
                result = original(*a, **kw); calls.append(str(a[0])); return result
            with mock.patch.object(f.guard, 'file', side_effect=count): f.commit()
        for failure_index in range(1, len(calls) + 1):
            with self.subTest(window=failure_index), Fixture() as f:
                count = [0]; original = f.guard.file
                def fail(*a, **kw):
                    value = original(*a, **kw); count[0] += 1
                    if count[0] == failure_index: raise OSError('injected durable boundary')
                    return value
                with mock.patch.object(f.guard, 'file', side_effect=fail):
                    with self.assertRaisesRegex(OSError, 'injected durable boundary'): f.commit()
                before = r.capture(reader)
                with self.assertRaisesRegex(ValueError, 'non-pristine'): r.require_pristine()
                self.assertEqual(r.capture(reader), before)
                self.assertEqual(reader.filesystem_receipt(r.TX), f.before[str(r.TX)])

    def test_directory_seal_append_and_installed_check_failure_windows(self):
        for method, occurrence in [('directory',1), ('directory',2), ('seal_snapshot',1), ('append',1)]:
            with self.subTest(method=method, occurrence=occurrence), Fixture() as f:
                original = getattr(f.guard, method); count = [0]
                def inject(*a, **kw):
                    value = original(*a, **kw); count[0] += 1
                    if count[0] == occurrence: raise OSError('injected boundary')
                    return value
                with mock.patch.object(f.guard, method, side_effect=inject):
                    with self.assertRaisesRegex(OSError, 'injected boundary'): f.commit()
                with self.assertRaisesRegex(ValueError, 'non-pristine'): r.require_pristine()
                self.assertEqual(reader.filesystem_receipt(r.TX), f.before[str(r.TX)])
        with Fixture() as f:
            with mock.patch.object(r, 'real_toolchain', side_effect=ValueError('installed toolchain rejected')):
                with self.assertRaisesRegex(ValueError, 'installed toolchain rejected'): f.commit()
            self.assertEqual(r.LEDGER.read_bytes(), f.raw[r.LEDGER])
            self.assertTrue(json.loads(r.STATE.read_bytes())['hard_stopped'])

    def test_stale_temporary_is_not_overwritten(self):
        with Fixture() as f:
            temp = r.STATE.with_name(r.STATE.name+'.mpi-recovery.tmp')
            temp.write_bytes(b'unknown')
            # Even if an unrelated caller accepts the new namespace, O_EXCL rejects the tmp.
            f.guard.expected = r.capture(reader)
            with self.assertRaises(FileExistsError):
                f.guard.file(r.STATE, f.target[r.STATE], 1000, 1000, 0o644, replace=True)
            self.assertEqual(temp.read_bytes(), b'unknown')
            self.assertEqual(r.STATE.read_bytes(), f.raw[r.STATE])

    def test_authority_no_execution_actions(self):
        for action in ('resume','permit','run','build','install'):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, 'no resume'):
                r.authority(['x',action,'x','x','x'])

    def test_partial_ledger_write_preserved_no_truncation_no_resume(self):
        with Fixture() as f:
            original_append = f.guard.append
            def partial(path, prefix, line):
                original_write = os.write
                count = [0]
                def inject(fd, data):
                    count[0] += 1
                    if count[0] > 1: raise OSError('partial event')
                    return original_write(fd, data[:17])
                with mock.patch.object(r.os, 'write', side_effect=inject):
                    original_append(path, prefix, line)
            with mock.patch.object(f.guard, 'append', side_effect=partial):
                with self.assertRaisesRegex(OSError, 'partial event'): f.commit()
            self.assertEqual(r.LEDGER.read_bytes(), f.raw[r.LEDGER] + f.line[:17])
            self.assertTrue(json.loads(r.STATE.read_bytes())['hard_stopped'])
            with self.assertRaisesRegex(ValueError, 'non-pristine'): r.require_pristine()

    def test_terminal_runtime_drift_rejected(self):
        with Fixture() as f:
            f.commit()
            with r.LEDGER.open('ab') as stream: stream.write(b'changed')
            with self.assertRaisesRegex(ValueError, 'namespace/identity drift'): f.guard.check()

    def test_invalid_failure_semantics_rejected(self):
        for field, value in [('state','SUCCESS_COMMITTED'), ('action','smoke_run'),
                             ('timed_out',True), ('exit_code',0), ('transaction_id','other')]:
            with self.subTest(field=field), Fixture() as f:
                raw = dict(f.raw); tx = json.loads(raw[r.TX]); tx[field] = value; raw[r.TX] = r.encode(tx)
                with self.assertRaisesRegex(ValueError, 'failure semantics'): r.targets(raw, 'utc', {})


if __name__ == '__main__':
    unittest.main()
