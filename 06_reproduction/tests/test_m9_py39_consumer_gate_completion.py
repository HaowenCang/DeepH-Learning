#!/usr/bin/env python3
"""Unit tests for the narrow consumer-gate completion receipt normalization."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "controllers/m9_py39_consumer_gate_completion.py"
specification = importlib.util.spec_from_file_location("gate_completion_tested", SCRIPT)
if specification is None or specification.loader is None:
    raise RuntimeError("cannot load completion controller")
completion = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = completion
specification.loader.exec_module(completion)


class CompletionReceiptTests(unittest.TestCase):
    def fixture(self) -> tuple[dict, dict]:
        runtime_active = {
            "path": "/active.json", "bytes": 10, "sha256": "a" * 64,
            "uid": 0, "gid": 1000, "mode": 0o640, "nlink": 1,
        }
        refresh = {
            "active": dict(runtime_active, dev=2096, ino=162490),
            "retired": {"sealed": True},
            "journal": {"state": "SUCCESS_COMMITTED"},
        }
        return refresh, {"active_overlap_gate_sha256": runtime_active}

    def test_normalizes_only_dev_and_ino_without_mutating_input(self) -> None:
        refresh, runtime = self.fixture()
        original = dict(refresh["active"])
        normalized = completion.normalized_refresh_for_gate(refresh, runtime)
        self.assertEqual(normalized["active"], runtime["active_overlap_gate_sha256"])
        self.assertEqual(refresh["active"], original)
        self.assertEqual(normalized["retired"], refresh["retired"])
        self.assertEqual(normalized["journal"], refresh["journal"])

    def test_rejects_shared_field_drift(self) -> None:
        refresh, runtime = self.fixture()
        refresh["active"]["sha256"] = "b" * 64
        with self.assertRaises(SystemExit):
            completion.normalized_refresh_for_gate(refresh, runtime)

    def test_rejects_any_other_field_delta_or_invalid_inode(self) -> None:
        for mutation in ("extra", "missing_dev", "zero_inode", "boolean_device"):
            with self.subTest(mutation=mutation):
                refresh, runtime = self.fixture()
                if mutation == "extra":
                    refresh["active"]["unexpected"] = True
                elif mutation == "missing_dev":
                    del refresh["active"]["dev"]
                elif mutation == "zero_inode":
                    refresh["active"]["ino"] = 0
                else:
                    refresh["active"]["dev"] = True
                with self.assertRaises(SystemExit):
                    completion.normalized_refresh_for_gate(refresh, runtime)


def directory_receipt(path: Path) -> dict:
    return {
        "path": path.as_posix(), "kind": "directory", "dev": 1, "ino": 2,
        "uid": 0, "gid": 1000, "mode": 0o750, "nlink": 2,
        "bytes": 4096, "mtime_ns": 1, "ctime_ns": 1,
    }


def gate_receipt(path: Path) -> dict:
    return {
        "path": path.as_posix(), "kind": "file", "dev": 1, "ino": 3,
        "uid": 0, "gid": 1000, "mode": 0o640, "nlink": 1,
        "bytes": 20, "mtime_ns": 2, "ctime_ns": 2,
        "sha256": "c" * 64,
    }


class TerminalReadTests(unittest.TestCase):
    def test_missing_snapshot_rejects_without_installer_call(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "missing"
            consumer = SimpleNamespace(SNAPSHOT_ROOT=root)
            consumer.read_snapshot_manifest = mock.Mock()
            installer = SimpleNamespace(
                consumer=consumer,
                STAGING_ROOT=Path(folder) / "staging",
            )
            with self.assertRaises(SystemExit):
                completion.read_terminal_snapshot(installer, {})
            consumer.read_snapshot_manifest.assert_not_called()

    def test_nonterminal_refresh_rejects_before_namespace_replay(self) -> None:
        installer = SimpleNamespace(
            verify_recovered_core=mock.Mock(return_value={"core": True}),
            read_bound_refresh_journal=mock.Mock(
                return_value=({"state": "ACTIVE_REPLACED"}, "d" * 64)
            ),
            validate_refresh_namespace=mock.Mock(),
            verify_installation_preflight=mock.Mock(),
        )
        with self.assertRaises(SystemExit):
            completion.read_terminal_refresh(installer, {"snapshot": True}, object())
        installer.validate_refresh_namespace.assert_not_called()
        installer.verify_installation_preflight.assert_not_called()

    def test_full_formal_snapshot_requires_two_equal_passes(self) -> None:
        with mock.patch.object(
            completion,
            "capture_formal_namespace_once",
            side_effect=[{"/formal": {"ino": 1}}, {"/formal": {"ino": 2}}],
        ):
            with self.assertRaises(SystemExit):
                completion.capture_formal_namespace(object())


class CompletionActionTests(unittest.TestCase):
    def fixture(self) -> tuple[object, dict, dict, dict, Path]:
        gate = Path("/formal/manifests/consumer-gate.json")
        consumer = SimpleNamespace(CONSUMER_GATE=gate)
        runtime_active = {
            "path": "/active.json", "bytes": 10, "sha256": "a" * 64,
            "uid": 0, "gid": 1000, "mode": 0o640, "nlink": 1,
        }
        consumer.consumer_runtime_receipts = mock.Mock(
            return_value={"active_overlap_gate_sha256": runtime_active}
        )
        installer = SimpleNamespace(
            consumer=consumer,
            verify_installation_guard=mock.Mock(),
            prepare_snapshot_for_refresh=mock.Mock(),
            refresh_active_overlap_gate=mock.Mock(),
            verify_installation_preflight=mock.Mock(),
            build_consumer_gate=mock.Mock(return_value={"gate": "expected"}),
            install_consumer_gate=mock.Mock(),
        )
        snapshot = {"receipt": {"sha256": "s" * 64}, "manifest": {}}
        refresh = {
            "active": dict(runtime_active, dev=2096, ino=162490),
            "retired": {"sealed": True},
            "journal": {"state": "SUCCESS_COMMITTED"},
        }
        core = {"core": True}
        installer.prepare_snapshot_for_refresh.return_value = (core, snapshot)
        installer.refresh_active_overlap_gate.return_value = refresh
        return installer, snapshot, refresh, core, gate

    def test_terminal_rejection_occurs_before_any_potential_mutator(self) -> None:
        installer, _, _, _, _ = self.fixture()
        with (
            mock.patch.object(
                completion, "read_terminal_snapshot",
                side_effect=SystemExit("snapshot missing"),
            ),
            mock.patch.object(completion, "capture_formal_namespace") as capture,
        ):
            with self.assertRaises(SystemExit):
                completion.run_completion_under_lock(
                    installer, {}, {}, object(), "preflight"
                )
        installer.prepare_snapshot_for_refresh.assert_not_called()
        installer.refresh_active_overlap_gate.assert_not_called()
        installer.install_consumer_gate.assert_not_called()
        capture.assert_not_called()

    def test_authorization_guard_rejects_before_terminal_or_mutator(self) -> None:
        installer, _, _, _, _ = self.fixture()
        installer.verify_installation_guard.side_effect = SystemExit(
            "authorization present"
        )
        with mock.patch.object(completion, "read_terminal_snapshot") as terminal:
            with self.assertRaises(SystemExit):
                completion.run_completion_under_lock(
                    installer, {}, {}, object(), "complete"
                )
        terminal.assert_not_called()
        installer.prepare_snapshot_for_refresh.assert_not_called()
        installer.refresh_active_overlap_gate.assert_not_called()
        installer.install_consumer_gate.assert_not_called()

    def test_preflight_is_zero_write_after_terminal_proof(self) -> None:
        installer, snapshot, refresh, core, gate = self.fixture()
        baseline = {gate.parent.as_posix(): directory_receipt(gate.parent)}
        with (
            mock.patch.object(
                completion, "read_terminal_snapshot", return_value=snapshot
            ),
            mock.patch.object(
                completion, "read_terminal_refresh", return_value=(core, refresh)
            ),
            mock.patch.object(
                completion, "capture_formal_namespace",
                side_effect=[baseline, baseline],
            ),
            mock.patch.object(completion.os.path, "lexists", return_value=False),
        ):
            result = completion.run_completion_under_lock(
                installer, {}, {}, object(), "preflight"
            )
        self.assertEqual(result["status"], "preflight_pass")
        installer.prepare_snapshot_for_refresh.assert_called_once()
        installer.refresh_active_overlap_gate.assert_called_once()
        installer.install_consumer_gate.assert_not_called()

    def test_preflight_detects_terminal_replay_write_before_gate_action(self) -> None:
        installer, snapshot, refresh, core, gate = self.fixture()
        baseline = {gate.parent.as_posix(): directory_receipt(gate.parent)}
        changed = dict(baseline)
        changed["/formal/unexpected"] = {"kind": "file"}
        with (
            mock.patch.object(
                completion, "read_terminal_snapshot", return_value=snapshot
            ),
            mock.patch.object(
                completion, "read_terminal_refresh", return_value=(core, refresh)
            ),
            mock.patch.object(
                completion, "capture_formal_namespace",
                side_effect=[baseline, changed],
            ),
            mock.patch.object(completion.os.path, "lexists", return_value=False),
        ):
            with self.assertRaises(SystemExit):
                completion.run_completion_under_lock(
                    installer, {}, {}, object(), "preflight"
                )
        installer.install_consumer_gate.assert_not_called()

    def test_complete_allows_only_first_consumer_gate_creation(self) -> None:
        installer, snapshot, refresh, core, gate = self.fixture()
        parent = directory_receipt(gate.parent)
        baseline = {gate.parent.as_posix(): parent}
        installed = gate_receipt(gate)
        receipt = {
            key: installed[key]
            for key in ("path", "bytes", "sha256", "uid", "gid", "mode", "nlink")
        }
        installer.install_consumer_gate.return_value = receipt
        completed = dict(baseline)
        completed[gate.as_posix()] = installed
        with (
            mock.patch.object(
                completion, "read_terminal_snapshot", return_value=snapshot
            ),
            mock.patch.object(
                completion, "read_terminal_refresh", return_value=(core, refresh)
            ),
            mock.patch.object(
                completion, "capture_formal_namespace",
                side_effect=[baseline, baseline, completed],
            ),
            mock.patch.object(completion.os.path, "lexists", return_value=False),
        ):
            result = completion.run_completion_under_lock(
                installer, {}, {}, object(), "complete"
            )
        self.assertEqual(result, {"status": "consumer_gate_completed", "receipt": receipt})

    def test_complete_existing_gate_must_be_exact_read_only_replay(self) -> None:
        installer, snapshot, refresh, core, gate = self.fixture()
        installed = gate_receipt(gate)
        baseline = {
            gate.parent.as_posix(): directory_receipt(gate.parent),
            gate.as_posix(): installed,
        }
        receipt = {
            key: installed[key]
            for key in ("path", "bytes", "sha256", "uid", "gid", "mode", "nlink")
        }
        installer.install_consumer_gate.return_value = receipt
        with (
            mock.patch.object(
                completion, "read_terminal_snapshot", return_value=snapshot
            ),
            mock.patch.object(
                completion, "read_terminal_refresh", return_value=(core, refresh)
            ),
            mock.patch.object(
                completion, "capture_formal_namespace",
                side_effect=[baseline, baseline, baseline],
            ),
            mock.patch.object(completion.os.path, "lexists", return_value=True),
        ):
            completion.run_completion_under_lock(
                installer, {}, {}, object(), "complete"
            )

    def test_write_set_rejects_any_second_path(self) -> None:
        gate = Path("/formal/manifests/consumer-gate.json")
        baseline = {gate.parent.as_posix(): directory_receipt(gate.parent)}
        installed = gate_receipt(gate)
        after = dict(baseline)
        after[gate.as_posix()] = installed
        after["/formal/manifests/unexpected"] = {"kind": "file"}
        receipt = {
            key: installed[key]
            for key in ("path", "bytes", "sha256", "uid", "gid", "mode", "nlink")
        }
        with self.assertRaises(SystemExit):
            completion.verify_completion_write_set(
                baseline, after, gate, receipt, False
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
