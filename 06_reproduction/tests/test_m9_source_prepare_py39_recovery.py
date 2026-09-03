#!/usr/bin/env python3
"""Synthetic crash/replay tests for the Python-3.9 source recovery."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import nullcontext


SCRIPT = Path(__file__).resolve().parents[1] / "controllers/m9_source_prepare_py39_recovery.py"
SPEC = importlib.util.spec_from_file_location("m9_source_prepare_py39_recovery", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load recovery controller")
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)


def write_json(path: Path, value: object, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(recovery.pretty_bytes(value))
    path.chmod(mode)


def build_fixture(root: Path) -> dict[str, object]:
    manifests = root / "manifests"
    control = root / "control"
    audits = root / "audits"
    project = root / "project"
    manifests.mkdir(); control.mkdir(); audits.mkdir(); project.mkdir()
    state = {
        "hard_stopped": True,
        "active_overlap_transaction": None,
        "last_event_utc": "failure",
        "cpu_seconds": {"overlap_build": 7.0, "other": 3.0},
        "cpu_adjustments": [{"credited_seconds": 2.0}],
        "gpu_seconds": {"compatibility": 1.0, "training": 0.0, "physical_validation": 0.0},
        "wall_clock_policy": {"mode": "UNLIMITED", "history": ["limited", "unlimited"]},
        "storage_history": [{"bytes": 1234}],
    }
    workflow = {"stage": "HARD_STOP", "hard_stopped": True, "active_transaction": None}
    txid = "a" * 32
    transaction = {"transaction_id": txid, "state": "FAILED_COMMITTED", "action": "source_prepare", "child_pid": 999999, "exit_code": 1, "timed_out": False, "start_utc": "start", "end_utc": "end", "failure_utc": "failure", "elapsed_seconds": 1.0, "reasons": ["overlap_command_failed"]}
    capability = {"transaction_id": txid, "state": "CONSUMED", "child_pid": 999999, "launcher_argv": ["/frozen/python3.9", "-I", "-S", "-B", "/frozen/m9_overlap_source_launcher.py", "--capability-id", "fixture"]}
    launcher = {"transaction_id": txid, "status": "FAIL"}
    ledger_prefix = b'{"event":"hard-stop"}\n'
    paths = {
        "lock": manifests / "lock",
        "state": manifests / "state.json",
        "workflow": manifests / "workflow.json",
        "ledger": manifests / "ledger.jsonl",
        "failure_transaction": manifests / "transaction.json",
        "consumed_capability": manifests / "cap.consumed.json",
        "launcher_receipt": manifests / "cap.launcher-receipt.json",
    }
    paths["lock"].write_bytes(b"")
    for name, value in (("state", state), ("workflow", workflow), ("failure_transaction", transaction), ("consumed_capability", capability), ("launcher_receipt", launcher)):
        write_json(paths[name], value)
    paths["ledger"].write_bytes(ledger_prefix)
    for path in paths.values():
        os.chown(path, 1000, 1000); path.chmod(0o644)
    paths["consumed_capability"].chmod(0o600); paths["launcher_receipt"].chmod(0o600)
    staging = root / "build.staging"
    (staging / "openmx3.9/source").mkdir(parents=True)
    (staging / "openmx3.9/source/makefile").write_bytes(b"makefile\n")
    source = project / "source.py"; source.write_bytes(b"VALUE=1\n")
    report = audits / "report.md"; report.write_bytes(b"PASS\n")
    work = audits / "work.md"; work.write_bytes(b"work\n")
    frozen = project / "frozen.json"
    write_json(frozen, {"schema_version": "m9-source-prepare-py39-recovery-frozen-v1", "files": {source.as_posix(): hashlib.sha256(source.read_bytes()).hexdigest()}})
    contract_path = project / "contract.json"
    expected_runtime = {}
    for name, path in paths.items():
        mode = 0o600 if name in {"consumed_capability", "launcher_receipt"} else 0o644
        expected_runtime[name] = recovery.exact_receipt(path, uid=1000, gid=1000, mode=mode)[0]
    staging_inventory = recovery.tree_inventory(staging)
    staging_inventory.update({"makefile_sha256": hashlib.sha256(b"makefile\n").hexdigest(), "independent_audit_inventory_sha256": "fixture"})
    contract = {
        "schema_version": "m9-source-prepare-py39-recovery-contract-v1",
        "recovery_id": "fixture-recovery",
        "failure_transaction_id": txid,
        "expected_runtime": expected_runtime,
        "ledger": {"bytes": len(ledger_prefix), "sha256": hashlib.sha256(ledger_prefix).hexdigest(), "prefix_bytes": 0, "prefix_sha256": hashlib.sha256(b"").hexdigest(), "failure_suffix_sha256": hashlib.sha256(ledger_prefix).hexdigest()},
        "staging_inventory": staging_inventory,
        "budget_invariants": {"raw_overlap_build_seconds": 7.0, "credited_seconds": 2.0, "wall_clock_mode": "UNLIMITED", "gpu_compatibility_seconds": 1.0, "gpu_training_seconds": 0.0, "gpu_physical_validation_seconds": 0.0},
        "products_required_absent": [(root / "absent-product").as_posix()],
    }
    write_json(contract_path, contract)
    verdict = audits / "verdict.json"
    verdict_value = {"schema_version": "m9-source-prepare-py39-recovery-verdict-v1", "decision_id": "D-018", "status": "PASS", "blocking": 0, "non_blocking": 0, "report_path": report.as_posix(), "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(), "work_package_path": work.as_posix(), "work_package_sha256": hashlib.sha256(work.read_bytes()).hexdigest(), "frozen_hashes_path": frozen.as_posix(), "frozen_hashes_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest()}
    write_json(verdict, verdict_value)
    retired = root / "build.retired"
    patches = {
        "FROZEN_PYTHON": Path(sys.executable), "CONTRACT": contract_path,
        "FROZEN_HASHES": frozen, "WORK_PACKAGE": work, "REPORT": report,
        "VERDICT": verdict, "GATE": control / "gate.json", "JOURNAL": control / "journal.json",
        "RECOVERY_TRANSACTION": control / "recovery.json", "FAILURE_TRANSACTION_SNAPSHOT": control / "failure.json",
        "LOCK": paths["lock"], "STATE": paths["state"], "WORKFLOW": paths["workflow"], "LEDGER": paths["ledger"],
        "FAILURE_TRANSACTION": paths["failure_transaction"], "STAGING": staging, "RETIRED": retired,
        "CAPABILITY": paths["consumed_capability"], "LAUNCHER_RECEIPT": paths["launcher_receipt"],
    }
    return {"paths": paths, "patches": patches, "staging": staging, "retired": retired, "state": state, "workflow": workflow, "ledger_prefix": ledger_prefix, "report": report, "contract": contract}


class SourcePreparePy39RecoveryTests(unittest.TestCase):
    def test_historical_child_pid_reuse_requires_exact_launcher_argv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            proc_root = Path(temporary)
            pid = 4242
            process = proc_root / str(pid)
            process.mkdir()
            expected = ["/frozen/python3.9", "-I", "-S", "-B", "/frozen/launcher.py"]
            (process / "cmdline").write_bytes(b"/bin/sh\0-c\0unrelated\0")
            self.assertFalse(
                recovery.process_matches_argv(pid, expected, proc_root=proc_root)
            )
            (process / "cmdline").write_bytes(
                b"\0".join(item.encode("utf-8") for item in expected) + b"\0"
            )
            self.assertTrue(
                recovery.process_matches_argv(pid, expected, proc_root=proc_root)
            )
            (process / "cmdline").write_bytes(
                b"\0".join(item.encode("utf-8") for item in expected) + b"\0\0"
            )
            self.assertFalse(
                recovery.process_matches_argv(pid, expected, proc_root=proc_root)
            )
            (process / "cmdline").write_bytes(
                expected[0].encode("utf-8")
                + b"\0\0"
                + b"\0".join(item.encode("utf-8") for item in expected[1:])
                + b"\0"
            )
            self.assertFalse(
                recovery.process_matches_argv(pid, expected, proc_root=proc_root)
            )
            expected_with_empty = [expected[0], "", *expected[1:]]
            (process / "cmdline").write_bytes(
                b"\0".join(item.encode("utf-8") for item in expected_with_empty) + b"\0"
            )
            self.assertTrue(
                recovery.process_matches_argv(
                    pid, expected_with_empty, proc_root=proc_root
                )
            )
            with self.assertRaises(ValueError):
                recovery.process_matches_argv(
                    pid, [expected[0], "invalid\0argument"], proc_root=proc_root
                )

    def test_exact_lf_writer_is_python39_compatible(self) -> None:
        common_path = SCRIPT.parents[1] / "scripts/m9_overlap_common.py"
        spec = importlib.util.spec_from_file_location("m9_overlap_common_py39", common_path)
        assert spec is not None and spec.loader is not None
        common = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(common)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "out.txt"
            common.write_utf8_lf(target, "one\ntwo\n")
            self.assertEqual(target.read_bytes(), b"one\ntwo\n")
            with self.assertRaises(ValueError):
                common.write_utf8_lf(target, "one\r\ntwo\r\n")

    def test_tree_inventory_binds_root_and_rejects_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "tree"
            (root / "directory").mkdir(parents=True)
            (root / "directory/file").write_bytes(b"payload")
            inventory = recovery.tree_inventory(root)
            self.assertEqual(inventory["directories"], 2)
            self.assertEqual(inventory["regular_files"], 1)
            self.assertEqual(inventory["records"], 3)
            (root / "link").symlink_to(root / "directory/file")
            with self.assertRaises(ValueError):
                recovery.tree_inventory(root)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_atomic_bytes_resumes_root_empty_and_owned_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.json"
            partial = root / "target.json.tmp"
            partial.write_bytes(b"")
            recovery.atomic_bytes(target, b"complete\n", uid=0, gid=0, mode=0o600)
            self.assertEqual(target.read_bytes(), b"complete\n")
            target.unlink()
            partial.write_bytes(b"comp")
            partial.chmod(0o600)
            recovery.atomic_bytes(target, b"complete\n", uid=0, gid=0, mode=0o600)
            self.assertEqual(target.read_bytes(), b"complete\n")

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_ledger_append_is_exactly_once_and_partial_resumable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Path(temporary) / "ledger.jsonl"
            prefix = b'{"event":"failure"}\n'
            event = b'{"event":"recovery"}\n'
            ledger.write_bytes(prefix + event[:7])
            os.chown(ledger, 1000, 1000)
            ledger.chmod(0o644)
            with mock.patch.object(recovery, "LEDGER", ledger):
                first = recovery.append_event_exact(prefix, event)
                second = recovery.append_event_exact(prefix, event)
            self.assertEqual(first, second)
            self.assertEqual(ledger.read_bytes(), prefix + event)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_full_recovery_and_terminal_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifests = root / "manifests"
            control = root / "control"
            audits = root / "audits"
            project = root / "project"
            manifests.mkdir(); control.mkdir(); audits.mkdir(); project.mkdir()
            state = {
                "hard_stopped": True,
                "active_overlap_transaction": None,
                "last_event_utc": "failure",
                "cpu_seconds": {"overlap_build": 7.0},
                "cpu_adjustments": [{"credited_seconds": 2.0}],
                "gpu_seconds": {"compatibility": 1.0, "training": 0.0, "physical_validation": 0.0},
                "wall_clock_policy": {"mode": "UNLIMITED"},
            }
            workflow = {"stage": "HARD_STOP", "hard_stopped": True, "active_transaction": None}
            txid = "a" * 32
            transaction = {"transaction_id": txid, "state": "FAILED_COMMITTED", "action": "source_prepare", "child_pid": 999999, "exit_code": 1, "timed_out": False, "start_utc": "start", "end_utc": "end", "failure_utc": "failure", "elapsed_seconds": 1.0, "reasons": ["overlap_command_failed"]}
            capability = {"transaction_id": txid, "state": "CONSUMED", "child_pid": 999999, "launcher_argv": ["/frozen/python3.9", "-I", "-S", "-B", "/frozen/m9_overlap_source_launcher.py", "--capability-id", "fixture"]}
            launcher = {"transaction_id": txid, "status": "FAIL"}
            ledger_prefix = b'{"event":"hard-stop"}\n'
            paths = {
                "lock": manifests / "lock",
                "state": manifests / "state.json",
                "workflow": manifests / "workflow.json",
                "ledger": manifests / "ledger.jsonl",
                "failure_transaction": manifests / "transaction.json",
                "consumed_capability": manifests / "cap.consumed.json",
                "launcher_receipt": manifests / "cap.launcher-receipt.json",
            }
            paths["lock"].write_bytes(b"")
            for name, value in (("state", state), ("workflow", workflow), ("failure_transaction", transaction), ("consumed_capability", capability), ("launcher_receipt", launcher)):
                write_json(paths[name], value)
            paths["ledger"].write_bytes(ledger_prefix)
            for path in paths.values():
                os.chown(path, 1000, 1000); path.chmod(0o644)
            paths["consumed_capability"].chmod(0o600); paths["launcher_receipt"].chmod(0o600)
            staging = root / "build.staging"
            (staging / "openmx3.9/source").mkdir(parents=True)
            (staging / "openmx3.9/source/makefile").write_bytes(b"makefile\n")
            source = project / "source.py"; source.write_bytes(b"VALUE=1\n")
            report = audits / "report.md"; report.write_bytes(b"PASS\n")
            work = audits / "work.md"; work.write_bytes(b"work\n")
            frozen = project / "frozen.json"
            write_json(frozen, {"schema_version": "m9-source-prepare-py39-recovery-frozen-v1", "files": {source.as_posix(): hashlib.sha256(source.read_bytes()).hexdigest()}})
            contract_path = project / "contract.json"
            expected_runtime = {}
            for name, path in paths.items():
                mode = 0o600 if name in {"consumed_capability", "launcher_receipt"} else 0o644
                receipt, _ = recovery.exact_receipt(path, uid=1000, gid=1000, mode=mode)
                expected_runtime[name] = receipt
            staging_inventory = recovery.tree_inventory(staging)
            staging_inventory.update({"makefile_sha256": hashlib.sha256(b"makefile\n").hexdigest(), "independent_audit_inventory_sha256": "fixture"})
            contract = {
                "schema_version": "m9-source-prepare-py39-recovery-contract-v1",
                "recovery_id": "fixture-recovery",
                "failure_transaction_id": txid,
                "expected_runtime": expected_runtime,
                "ledger": {"bytes": len(ledger_prefix), "sha256": hashlib.sha256(ledger_prefix).hexdigest(), "prefix_bytes": 0, "prefix_sha256": hashlib.sha256(b"").hexdigest(), "failure_suffix_sha256": hashlib.sha256(ledger_prefix).hexdigest()},
                "staging_inventory": staging_inventory,
                "budget_invariants": {"raw_overlap_build_seconds": 7.0, "credited_seconds": 2.0, "wall_clock_mode": "UNLIMITED", "gpu_compatibility_seconds": 1.0, "gpu_training_seconds": 0.0, "gpu_physical_validation_seconds": 0.0},
                "products_required_absent": [(root / "absent-product").as_posix()],
            }
            write_json(contract_path, contract)
            verdict = audits / "verdict.json"
            verdict_value = {"schema_version": "m9-source-prepare-py39-recovery-verdict-v1", "decision_id": "D-018", "status": "PASS", "blocking": 0, "non_blocking": 0, "report_path": report.as_posix(), "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(), "work_package_path": work.as_posix(), "work_package_sha256": hashlib.sha256(work.read_bytes()).hexdigest(), "frozen_hashes_path": frozen.as_posix(), "frozen_hashes_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest()}
            write_json(verdict, verdict_value)
            lock = paths["lock"]
            retired = root / "build.retired"
            patches = {
                "FROZEN_PYTHON": Path(sys.executable), "CONTRACT": contract_path,
                "FROZEN_HASHES": frozen, "WORK_PACKAGE": work, "REPORT": report,
                "VERDICT": verdict, "GATE": control / "gate.json", "JOURNAL": control / "journal.json",
                "RECOVERY_TRANSACTION": control / "recovery.json", "FAILURE_TRANSACTION_SNAPSHOT": control / "failure.json",
                "LOCK": lock, "STATE": paths["state"], "WORKFLOW": paths["workflow"], "LEDGER": paths["ledger"],
                "FAILURE_TRANSACTION": paths["failure_transaction"], "STAGING": staging, "RETIRED": retired,
                "CAPABILITY": paths["consumed_capability"], "LAUNCHER_RECEIPT": paths["launcher_receipt"],
            }
            with mock.patch.multiple(recovery, **patches):
                self.assertEqual(recovery.create_gate(), 0)
                self.assertEqual(recovery.recover(), 0)
                terminal = recovery.RECOVERY_TRANSACTION.read_bytes()
                self.assertEqual(recovery.recover(), 0)
                self.assertEqual(recovery.RECOVERY_TRANSACTION.read_bytes(), terminal)
                self.assertFalse(staging.exists())
                self.assertTrue(retired.is_dir())
                self.assertFalse(json.loads(paths["state"].read_text())["hard_stopped"])
                self.assertEqual(json.loads(paths["workflow"].read_text())["stage"], "AUDIT_PASSED")

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_terminal_replay_rejects_link_metadata_and_inode_drift(self) -> None:
        mutations = ("state_symlink", "workflow_hardlink", "ledger_mode", "state_inode")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                fixture = build_fixture(Path(temporary))
                paths = fixture["paths"]
                assert isinstance(paths, dict)
                patches = fixture["patches"]
                assert isinstance(patches, dict)
                with mock.patch.multiple(recovery, **patches):
                    recovery.create_gate(); recovery.recover()
                    journal_before = recovery.JOURNAL.read_bytes()
                    transaction_before = recovery.RECOVERY_TRANSACTION.read_bytes()
                    if mutation == "state_symlink":
                        payload = recovery.STATE.read_bytes()
                        replacement = recovery.STATE.with_name("state-target.json")
                        replacement.write_bytes(payload); os.chown(replacement, 1000, 1000); replacement.chmod(0o644)
                        recovery.STATE.unlink(); recovery.STATE.symlink_to(replacement)
                    elif mutation == "workflow_hardlink":
                        os.link(recovery.WORKFLOW, recovery.WORKFLOW.with_name("workflow-link.json"))
                    elif mutation == "ledger_mode":
                        recovery.LEDGER.chmod(0o666)
                    else:
                        replacement = recovery.STATE.with_name("state-replacement.json")
                        replacement.write_bytes(recovery.STATE.read_bytes()); os.chown(replacement, 1000, 1000); replacement.chmod(0o644)
                        os.replace(replacement, recovery.STATE)
                    with self.assertRaises((OSError, ValueError)):
                        recovery.recover()
                    self.assertEqual(recovery.JOURNAL.read_bytes(), journal_before)
                    self.assertEqual(recovery.RECOVERY_TRANSACTION.read_bytes(), transaction_before)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_budget_lock_identity_drift_is_zero_write_rejected(self) -> None:
        for mutation in ("symlink", "hardlink", "mode", "inode"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                fixture = build_fixture(Path(temporary))
                paths = fixture["paths"]
                patches = fixture["patches"]
                assert isinstance(paths, dict) and isinstance(patches, dict)
                with mock.patch.multiple(recovery, **patches):
                    recovery.create_gate()
                    state_before = recovery.STATE.read_bytes()
                    ledger_before = recovery.LEDGER.read_bytes()
                    staging_before = recovery.tree_inventory(recovery.STAGING)
                    if mutation == "symlink":
                        decoy = recovery.LOCK.with_name("lock-decoy"); decoy.write_bytes(b""); os.chown(decoy, 1000, 1000); decoy.chmod(0o644)
                        recovery.LOCK.unlink(); recovery.LOCK.symlink_to(decoy)
                    elif mutation == "hardlink":
                        os.link(recovery.LOCK, recovery.LOCK.with_name("lock-link"))
                    elif mutation == "mode":
                        recovery.LOCK.chmod(0o666)
                    else:
                        decoy = recovery.LOCK.with_name("lock-new"); decoy.write_bytes(b""); os.chown(decoy, 1000, 1000); decoy.chmod(0o644)
                        os.replace(decoy, recovery.LOCK)
                    with self.assertRaises((OSError, ValueError)):
                        recovery.recover()
                    self.assertEqual(recovery.STATE.read_bytes(), state_before)
                    self.assertEqual(recovery.LEDGER.read_bytes(), ledger_before)
                    self.assertEqual(recovery.tree_inventory(recovery.STAGING), staging_before)
                    self.assertFalse(os.path.lexists(recovery.JOURNAL))

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_gate_scope_report_verdict_work_package_and_frozen_drift_are_zero_write(self) -> None:
        for mutation in ("gate_scope", "report", "verdict", "work_package", "frozen"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
                assert isinstance(patches, dict)
                with mock.patch.multiple(recovery, **patches):
                    recovery.create_gate()
                    state_before = recovery.STATE.read_bytes(); ledger_before = recovery.LEDGER.read_bytes()
                    if mutation == "gate_scope":
                        gate = json.loads(recovery.GATE.read_text()); gate["scope"] = "ALLOW_SOURCE_PREPARE"
                        write_json(recovery.GATE, gate, 0o600)
                    elif mutation == "report":
                        recovery.REPORT.write_bytes(b"changed report\n")
                    elif mutation == "verdict":
                        verdict = json.loads(recovery.VERDICT.read_text()); verdict["status"] = "FAIL"
                        write_json(recovery.VERDICT, verdict)
                    elif mutation == "work_package":
                        recovery.WORK_PACKAGE.write_bytes(b"changed work package\n")
                    else:
                        recovery.FROZEN_HASHES.write_bytes(b"{}\n")
                    with self.assertRaises((ValueError, KeyError)):
                        recovery.recover()
                    self.assertEqual(recovery.STATE.read_bytes(), state_before)
                    self.assertEqual(recovery.LEDGER.read_bytes(), ledger_before)
                    self.assertFalse(os.path.lexists(recovery.JOURNAL))

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_all_atomic_json_crash_windows_resume_exactly_once(self) -> None:
        class SimulatedPowerLoss(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as temporary:
            fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
            assert isinstance(patches, dict)
            with mock.patch.multiple(recovery, **patches):
                recovery.create_gate()
                real_atomic_json = recovery.atomic_json
                calls = {"count": 0}
                def count_atomic(path: Path, value: object, *, uid: int, gid: int, mode: int) -> None:
                    calls["count"] += 1
                    real_atomic_json(path, value, uid=uid, gid=gid, mode=mode)
                with mock.patch.object(recovery, "atomic_json", side_effect=count_atomic):
                    recovery.recover()
                total = calls["count"]
        self.assertGreaterEqual(total, 14)
        for cut in range(1, total + 1):
            with self.subTest(cut=cut), tempfile.TemporaryDirectory() as temporary:
                fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
                assert isinstance(patches, dict)
                with mock.patch.multiple(recovery, **patches):
                    recovery.create_gate()
                    real_atomic_json = recovery.atomic_json
                    calls = {"count": 0}
                    def fail_atomic(path: Path, value: object, *, uid: int, gid: int, mode: int) -> None:
                        calls["count"] += 1
                        real_atomic_json(path, value, uid=uid, gid=gid, mode=mode)
                        if calls["count"] == cut:
                            raise SimulatedPowerLoss(str(cut))
                    with mock.patch.object(recovery, "atomic_json", side_effect=fail_atomic):
                        with self.assertRaises(SimulatedPowerLoss):
                            recovery.recover()
                    recovery.recover()
                    terminal = recovery.RECOVERY_TRANSACTION.read_bytes()
                    terminal_mtime = os.lstat(recovery.RECOVERY_TRANSACTION).st_mtime_ns
                    recovery.recover()
                    self.assertEqual(recovery.RECOVERY_TRANSACTION.read_bytes(), terminal)
                    self.assertEqual(os.lstat(recovery.RECOVERY_TRANSACTION).st_mtime_ns, terminal_mtime)
                    self.assertEqual(recovery.LEDGER.read_bytes().count(b'OVERLAP_SOURCE_PREPARE_PY39_RECOVERY'), 1)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_snapshot_state_workflow_and_rename_crash_windows_resume(self) -> None:
        class SimulatedPowerLoss(RuntimeError):
            pass
        targets = ("snapshot", "state", "workflow", "rename")
        for target in targets:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
                assert isinstance(patches, dict)
                with mock.patch.multiple(recovery, **patches):
                    recovery.create_gate()
                    if target == "rename":
                        real_replace = recovery.os.replace
                        fired = {"value": False}
                        def fail_replace(source: object, destination: object) -> None:
                            real_replace(source, destination)
                            if Path(source) == recovery.STAGING and Path(destination) == recovery.RETIRED and not fired["value"]:
                                fired["value"] = True
                                raise SimulatedPowerLoss("rename")
                        context = mock.patch.object(recovery.os, "replace", side_effect=fail_replace)
                    else:
                        real_atomic_bytes = recovery.atomic_bytes
                        target_path = {"snapshot": recovery.FAILURE_TRANSACTION_SNAPSHOT, "state": recovery.STATE, "workflow": recovery.WORKFLOW}[target]
                        fired = {"value": False}
                        def fail_bytes(path: Path, payload: bytes, *, uid: int, gid: int, mode: int) -> None:
                            real_atomic_bytes(path, payload, uid=uid, gid=gid, mode=mode)
                            if path == target_path and not fired["value"]:
                                fired["value"] = True
                                raise SimulatedPowerLoss(target)
                        context = mock.patch.object(recovery, "atomic_bytes", side_effect=fail_bytes)
                    with context:
                        with self.assertRaises(SimulatedPowerLoss):
                            recovery.recover()
                    recovery.recover()
                    self.assertEqual(json.loads(recovery.JOURNAL.read_text())["state"], "SUCCESS_COMMITTED")
                    self.assertEqual(recovery.LEDGER.read_bytes().count(b'OVERLAP_SOURCE_PREPARE_PY39_RECOVERY'), 1)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_workflow_committed_is_persisted_before_terminal(self) -> None:
        class SimulatedPowerLoss(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as temporary:
            fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
            assert isinstance(patches, dict)
            with mock.patch.multiple(recovery, **patches):
                recovery.create_gate(); real_atomic_json = recovery.atomic_json
                def stop_at_workflow(path: Path, value: object, *, uid: int, gid: int, mode: int) -> None:
                    real_atomic_json(path, value, uid=uid, gid=gid, mode=mode)
                    if path == recovery.RECOVERY_TRANSACTION and isinstance(value, dict) and value.get("state") == "WORKFLOW_COMMITTED":
                        raise SimulatedPowerLoss("workflow committed")
                with mock.patch.object(recovery, "atomic_json", side_effect=stop_at_workflow):
                    with self.assertRaises(SimulatedPowerLoss):
                        recovery.recover()
                self.assertEqual(json.loads(recovery.JOURNAL.read_text())["state"], "WORKFLOW_COMMITTED")
                self.assertEqual(json.loads(recovery.RECOVERY_TRANSACTION.read_text())["state"], "WORKFLOW_COMMITTED")
                recovery.recover()
                self.assertEqual(json.loads(recovery.JOURNAL.read_text())["state"], "SUCCESS_COMMITTED")

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_committed_post_receipts_cannot_be_rebound_during_resume(self) -> None:
        class SimulatedPowerLoss(RuntimeError):
            pass
        cases = (
            ("LEDGER_COMMITTED", "ledger"),
            ("STATE_COMMITTED", "state"),
            ("WORKFLOW_COMMITTED", "workflow"),
        )
        for phase, name in cases:
            for mutation in ("inode", "symlink", "hardlink", "mode", "owner"):
                with self.subTest(phase=phase, mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                    fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
                    assert isinstance(patches, dict)
                    with mock.patch.multiple(recovery, **patches):
                        recovery.create_gate(); real_atomic_json = recovery.atomic_json
                        def stop_at_phase(path: Path, value: object, *, uid: int, gid: int, mode: int) -> None:
                            real_atomic_json(path, value, uid=uid, gid=gid, mode=mode)
                            if path == recovery.RECOVERY_TRANSACTION and isinstance(value, dict) and value.get("state") == phase:
                                raise SimulatedPowerLoss(phase)
                        with mock.patch.object(recovery, "atomic_json", side_effect=stop_at_phase):
                            with self.assertRaises(SimulatedPowerLoss):
                                recovery.recover()
                        target = {"ledger": recovery.LEDGER, "state": recovery.STATE, "workflow": recovery.WORKFLOW}[name]
                        journal_before = recovery.JOURNAL.read_bytes(); transaction_before = recovery.RECOVERY_TRANSACTION.read_bytes()
                        if mutation in {"inode", "symlink"}:
                            replacement = target.with_name(target.name + ".replacement")
                            replacement.write_bytes(target.read_bytes()); os.chown(replacement, 1000, 1000); replacement.chmod(0o644)
                            target.unlink()
                            if mutation == "inode":
                                os.replace(replacement, target)
                            else:
                                target.symlink_to(replacement)
                        elif mutation == "hardlink":
                            os.link(target, target.with_name(target.name + ".hardlink"))
                        elif mutation == "mode":
                            target.chmod(0o666)
                        else:
                            os.chown(target, 0, 0)
                        with self.assertRaises((OSError, ValueError)):
                            recovery.recover()
                        self.assertEqual(recovery.JOURNAL.read_bytes(), journal_before)
                        self.assertEqual(recovery.RECOVERY_TRANSACTION.read_bytes(), transaction_before)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_invalid_phase_pairs_and_orphan_transaction_are_zero_write_rejected(self) -> None:
        class SimulatedPowerLoss(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as temporary:
            fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
            assert isinstance(patches, dict)
            with mock.patch.multiple(recovery, **patches):
                recovery.create_gate(); real_atomic_json = recovery.atomic_json
                def stop_at_state(path: Path, value: object, *, uid: int, gid: int, mode: int) -> None:
                    real_atomic_json(path, value, uid=uid, gid=gid, mode=mode)
                    if path == recovery.RECOVERY_TRANSACTION and isinstance(value, dict) and value.get("state") == "STATE_COMMITTED":
                        raise SimulatedPowerLoss("state")
                with mock.patch.object(recovery, "atomic_json", side_effect=stop_at_state):
                    with self.assertRaises(SimulatedPowerLoss):
                        recovery.recover()
                journal_before = recovery.JOURNAL.read_bytes()
                transaction = json.loads(recovery.RECOVERY_TRANSACTION.read_text()); transaction["state"] = "PREPARED"
                write_json(recovery.RECOVERY_TRANSACTION, transaction, 0o600)
                transaction_before = recovery.RECOVERY_TRANSACTION.read_bytes()
                with self.assertRaises(ValueError):
                    recovery.recover()
                self.assertEqual(recovery.JOURNAL.read_bytes(), journal_before)
                self.assertEqual(recovery.RECOVERY_TRANSACTION.read_bytes(), transaction_before)
        with tempfile.TemporaryDirectory() as temporary:
            fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
            assert isinstance(patches, dict)
            with mock.patch.multiple(recovery, **patches):
                recovery.create_gate()
                write_json(recovery.RECOVERY_TRANSACTION, {"state": "PREPARED"}, 0o600)
                with self.assertRaises(ValueError):
                    recovery.recover()
                self.assertFalse(os.path.lexists(recovery.JOURNAL))

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_retirement_four_states_snapshot_drift_and_budget_history(self) -> None:
        for disposition in ("both", "neither", "retired_only", "retired_symlink"):
            with self.subTest(disposition=disposition), tempfile.TemporaryDirectory() as temporary:
                fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
                assert isinstance(patches, dict)
                with mock.patch.multiple(recovery, **patches):
                    recovery.create_gate()
                    if disposition == "both":
                        recovery.RETIRED.mkdir()
                    elif disposition == "neither":
                        os.replace(recovery.STAGING, recovery.STAGING.with_name("unbound"))
                    elif disposition == "retired_only":
                        os.replace(recovery.STAGING, recovery.RETIRED)
                    else:
                        target = recovery.RETIRED.with_name("retired-target"); target.mkdir()
                        recovery.RETIRED.symlink_to(target, target_is_directory=True)
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        recovery.recover()
        with tempfile.TemporaryDirectory() as temporary:
            fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
            assert isinstance(patches, dict)
            with mock.patch.multiple(recovery, **patches):
                recovery.create_gate()
                pre = fixture["state"]
                assert isinstance(pre, dict)
                recovery.recover()
                post = json.loads(recovery.STATE.read_text())
                for key in ("cpu_seconds", "cpu_adjustments", "gpu_seconds", "wall_clock_policy", "storage_history"):
                    self.assertEqual(post[key], pre[key])
        with tempfile.TemporaryDirectory() as temporary:
            fixture = build_fixture(Path(temporary)); patches = fixture["patches"]
            assert isinstance(patches, dict)
            with mock.patch.multiple(recovery, **patches):
                recovery.create_gate()
                recovery.FAILURE_TRANSACTION_SNAPSHOT.write_bytes(b"drift\n"); recovery.FAILURE_TRANSACTION_SNAPSHOT.chmod(0o600)
                with self.assertRaises(ValueError):
                    recovery.recover()

    def test_build_and_input_full_paths_use_python39_lf_writer(self) -> None:
        scripts = SCRIPT.parents[1] / "scripts"
        site_packages = Path(sys.executable).resolve().parents[1] / "lib/python3.9/site-packages"
        sys.path.insert(0, str(site_packages))
        sys.path.insert(0, str(scripts))
        try:
            modules = {}
            for name in ("m9_openmx_build", "m9_openmx_input"):
                spec = importlib.util.spec_from_file_location(name + "_recovery_test", scripts / (name + ".py"))
                assert spec is not None and spec.loader is not None
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); modules[name] = module
        finally:
            sys.path.pop(0)
            sys.path.pop(0)
        class StopAfterWrite(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); build = modules["m9_openmx_build"]
            mapping = {"openmx_build_root": root / "build", "source_downloads": root / "downloads", "hdf5_prefix": root / "hdf5"}
            mapping["source_downloads"].mkdir()
            def fake_extract(archive: Path, destination: Path) -> None:
                if archive.name == "openmx3.9.tar.gz":
                    (destination / "openmx3.9/source").mkdir(parents=True)
                    (destination / "openmx3.9/source/makefile").write_bytes(b"original\n")
                else:
                    destination.mkdir(parents=True)
            archive = {"bytes": 0, "sha256": "fixture"}
            contract = {"software": {"openmx_base": archive, "openmx_official_patch": archive, "hdf5": archive, "openmx_makefile": {}}}
            with mock.patch.multiple(build, require_budget_wrapper=lambda _: None, verify_frozen_project_files=lambda _: None, verify_static_sources=lambda _: {}, workflow_lock=lambda: nullcontext(), load_workflow_state=lambda _: {"stage": "AUDIT_PASSED", "hard_stopped": False}, runtime_path=lambda _c, key: mapping[key], verify_archive=lambda *_: None, safe_extract=fake_extract, apply_official_patch=lambda *_: [], render_makefile=lambda *_: "alpha β\n", source_files_for_manifest=mock.Mock(side_effect=StopAfterWrite)):
                with self.assertRaises(StopAfterWrite):
                    build.prepare_sources(contract)
            self.assertEqual((root / "build.staging/openmx3.9/source/makefile").read_bytes(), "alpha β\n".encode("utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); input_module = modules["m9_openmx_input"]
            processed = root / "processed"; (processed / "s").mkdir(parents=True)
            run_root = root / "runs"; run_root.mkdir()
            build_manifest = root / "build.json"; build_manifest.write_bytes(b"{}\n")
            mapping = {"processed_data": processed, "run_root": run_root, "openmx_data": root / "data", "build_manifest": build_manifest}
            contract = {"execution": {"smoke_structure_id": "s"}}
            loaded = {"lattice": [], "fractional": [], "cartesian": []}
            with mock.patch.multiple(input_module, expected_structure_ids=lambda _: ["s"], verify_frozen_project_files=lambda _: None, verify_basis=lambda _: {}, workflow_lock=lambda: nullcontext(), load_workflow_state=lambda _: {"stage": "BUILD_PASSED", "hard_stopped": False, "completed_structure_ids": [], "next_structure_id": "s"}, require_budget_wrapper=lambda _: None, runtime_path=lambda _c, key: mapping[key], load_structure=lambda *_: loaded, render_input=lambda *_: "gamma δ\n", verify_rendered_input=mock.Mock(side_effect=StopAfterWrite)):
                with self.assertRaises(StopAfterWrite):
                    input_module.prepare_structure("s", contract, "contract-hash")
            self.assertEqual((run_root / ".s.preparing/openmx.dat").read_bytes(), "gamma δ\n".encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
