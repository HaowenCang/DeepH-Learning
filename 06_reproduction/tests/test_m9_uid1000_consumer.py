#!/usr/bin/env python3
"""Synthetic security matrix for the D-018 UID1000 consumer adapter."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


TEST_PATH = Path(__file__).resolve()
REPRODUCTION = TEST_PATH.parents[1]
ADAPTER_PATH = REPRODUCTION / "controllers/m9_budget_uid1000_consumer.py"
INSTALLER_PATH = REPRODUCTION / "controllers/m9_uid1000_consumer_install.py"
BOOTSTRAP_PATH = REPRODUCTION / "controllers/m9_uid1000_consumer_bootstrap.py"


def load_module(name: str, path: Path) -> object:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


adapter = load_module("m9_uid1000_consumer_tested", ADAPTER_PATH)
OPERATION_ID = "a" * 32


def source_prepare_argv(operation_id: str = OPERATION_ID) -> list[str]:
    return [
        "run",
        "--consumer-operation-id", operation_id,
        "--bucket", "none",
        "--cpu-bucket", "overlap_build",
        "--forecast-bytes", "1073741824",
        "--overlap-operation",
        "--overlap-action", "source_prepare",
        "--config", (REPRODUCTION / "configs/m9_overlap_only_contract.json").as_posix(),
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def set_metadata(path: Path, uid: int, gid: int, mode: int) -> None:
    os.chown(path, uid, gid)
    os.chmod(path, mode)


class UID1000ConsumerTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[contextlib.ExitStack, dict[str, object]]:
        os.chown(root, 0, 0)
        os.chmod(root, 0o755)
        snapshot_root = root / "consumer-snapshot"
        snapshot_root.mkdir()
        set_metadata(snapshot_root, 0, 1000, 0o550)

        historical_bootstrap_root = root / "historical-bootstrap"
        historical_bootstrap_root.mkdir()
        historical_bootstrap_member = historical_bootstrap_root / "old-adapter.py"
        historical_bootstrap_member.write_text("# historical bootstrap\n", encoding="utf-8")
        set_metadata(historical_bootstrap_member, 0, 1000, 0o440)
        historical_bootstrap_receipt = historical_bootstrap_root / "bootstrap_receipt.json"
        write_json(historical_bootstrap_receipt, {
            "schema_version": "m9-uid1000-consumer-bootstrap-v1",
            "decision_id": "D-018",
            "frozen_hashes_sha256": "f" * 64,
            "members": {
                historical_bootstrap_member.as_posix(): {
                    "sha256": sha256(historical_bootstrap_member),
                    "bytes": historical_bootstrap_member.stat().st_size,
                }
            },
        })
        set_metadata(historical_bootstrap_receipt, 0, 1000, 0o440)
        set_metadata(historical_bootstrap_root, 0, 1000, 0o550)

        historical_snapshot_root = root / "historical-snapshot"
        historical_snapshot_root.mkdir()
        historical_snapshot_member = historical_snapshot_root / "old-controller.py"
        historical_snapshot_member.write_text("# historical snapshot\n", encoding="utf-8")
        set_metadata(historical_snapshot_member, 0, 1000, 0o440)
        historical_snapshot_manifest = historical_snapshot_root / "snapshot_manifest.json"
        write_json(historical_snapshot_manifest, {
            "schema_version": "m9-uid1000-consumer-snapshot-v1",
            "decision_id": "D-018",
            "issue_id": "D018-EGF-B01",
            "files": {
                "/project/old-controller.py": {
                    "snapshot_path": historical_snapshot_member.as_posix(),
                    "sha256": sha256(historical_snapshot_member),
                    "bytes": historical_snapshot_member.stat().st_size,
                }
            },
        })
        set_metadata(historical_snapshot_manifest, 0, 1000, 0o440)
        set_metadata(historical_snapshot_root, 0, 1000, 0o550)

        historical_consumer_gate = root / "historical-consumer-gate.json"
        write_json(historical_consumer_gate, {"schema_version": "historical", "status": "PASS"})
        set_metadata(historical_consumer_gate, 0, 1000, 0o640)

        names = (
            "state", "workflow", "ledger", "overlap_tx", "source_tx",
            "source_gate", "d018_gate", "d018_tx", "execution_gate",
            "active_gate", "consumer_gate", "consumer_verdict", "frozen",
            "recovery_fact", "recovery_verdict", "work_package",
            "consumer_report", "journal",
            "pre_state_snapshot", "control", "authorization", "authorization_record",
        )
        paths = {name: root / f"{name}.json" for name in names}
        snapshot_manifest = snapshot_root / "snapshot_manifest.json"
        snapshot_controller = snapshot_root / "m9_budget.py"
        shutil.copyfile(adapter.PROJECT_ORIGINAL_CONTROLLER, snapshot_controller)
        set_metadata(snapshot_controller, 0, 1000, 0o440)

        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch.multiple(
            adapter,
            SNAPSHOT_ROOT=snapshot_root,
            SNAPSHOT_MANIFEST=snapshot_manifest,
            INSTALLED_ADAPTER=ADAPTER_PATH,
            ORIGINAL_CONTROLLER=snapshot_controller,
            HISTORICAL_CONSUMER_GATE=historical_consumer_gate,
            HISTORICAL_BOOTSTRAP_ROOT=historical_bootstrap_root,
            HISTORICAL_BOOTSTRAP_RECEIPT=historical_bootstrap_receipt,
            HISTORICAL_SNAPSHOT_ROOT=historical_snapshot_root,
            HISTORICAL_SNAPSHOT_MANIFEST=historical_snapshot_manifest,
            EXPECTED_HISTORICAL_CONSUMER_GATE_SHA256=sha256(historical_consumer_gate),
            EXPECTED_HISTORICAL_BOOTSTRAP_RECEIPT_SHA256=sha256(
                historical_bootstrap_receipt
            ),
            EXPECTED_HISTORICAL_SNAPSHOT_MANIFEST_SHA256=sha256(
                historical_snapshot_manifest
            ),
        ))
        adapter._M9 = None
        m9 = adapter.original_controller()

        state = {
            "schema_version": "m9-budget-state-v1",
            "start_utc": m9.FROZEN_START,
            "deadline_utc": m9.FROZEN_DEADLINE,
            "vhdx_baseline_bytes": 0,
            "gpu_seconds": {key: 0.0 for key in m9.GPU_LIMITS},
            "cpu_seconds": {key: 0.0 for key in m9.CPU_LIMITS},
            "cpu_adjustments": [],
            "hard_stopped": False,
            "active_overlap_transaction": None,
            "wall_clock_policy": {
                "mode": "UNLIMITED",
                "decision_id": "D-018",
                "historical_limit_seconds": m9.HISTORICAL_WALL_LIMIT,
                "historical_start_utc": m9.FROZEN_START,
                "historical_deadline_utc": m9.FROZEN_DEADLINE,
                "migration_transaction_id": "d018-unlimited-wall-clock-20260820-01",
                "migration_event_id":
                    "d018-unlimited-wall-clock-20260820-01:unlimited-wall-clock",
                "authorization_sha256": "a" * 64,
                "contract_sha256": "c" * 64,
                "gate_sha256": "1" * 64,
            },
        }
        workflow = {
            "schema_version": "m9-overlap-workflow-state-v1",
            "stage": "AUDIT_PASSED",
            "apt_install_completed": True,
            "hard_stopped": False,
            "active_transaction": None,
        }
        values = {
            "state": state,
            "workflow": workflow,
            "overlap_tx": {"state": "SUCCESS_COMMITTED"},
            "source_tx": {"state": "SUCCESS_COMMITTED"},
            "d018_gate": {"status": "PASS"},
            "d018_tx": {
                "schema_version": "m9-unlimited-wall-clock-transaction-v1",
                "state": "SUCCESS_COMMITTED",
            },
            "active_gate": {"status": "PASS"},
        }
        for name, value in values.items():
            write_json(paths[name], value)
        paths["ledger"].write_text('{"event":"prior"}\n', encoding="utf-8")
        paths["recovery_fact"].write_text("# recovery PASS\n", encoding="utf-8")
        write_json(
            paths["recovery_verdict"],
            {"status": "PASS", "blocking": 0, "non_blocking": 0},
        )
        paths["work_package"].write_text("# work package\n", encoding="utf-8")
        paths["consumer_report"].write_text("# PASS\n", encoding="utf-8")
        paths["control"].write_text("frozen\n", encoding="utf-8")

        for name in ("state", "workflow", "ledger", "overlap_tx", "source_tx"):
            set_metadata(paths[name], 1000, 1000, 0o644)
        for name in ("d018_gate", "d018_tx", "active_gate"):
            set_metadata(paths[name], 0, 1000, 0o640)
        for name in ("source_gate", "journal", "pre_state_snapshot"):
            write_json(paths[name], {"root_private": True})
            set_metadata(paths[name], 0, 0, 0o600)

        execution_runtime = {
            "state_sha256": sha256(paths["state"]),
            "workflow_sha256": sha256(paths["workflow"]),
            "ledger_sha256": sha256(paths["ledger"]),
            "overlap_transaction_sha256": sha256(paths["overlap_tx"]),
            "source_control_recovery_transaction_sha256": sha256(paths["source_tx"]),
            "source_control_recovery_gate_sha256": sha256(paths["source_gate"]),
            "d018_gate_sha256": sha256(paths["d018_gate"]),
            "d018_transaction_sha256": sha256(paths["d018_tx"]),
            "d018_journal_sha256": sha256(paths["journal"]),
            "d018_pre_state_snapshot_sha256": sha256(paths["pre_state_snapshot"]),
            "retired_overlap_gate_sha256": "9" * 64,
            "active_overlap_gate_sha256": sha256(paths["active_gate"]),
            "source_products_present": [],
        }
        execution_gate = {
            "schema_version": "m9-unlimited-wall-clock-execution-gate-v1",
            "decision_id": "D-018",
            "status": "PASS",
            "blocking": 0,
            "non_blocking": 0,
            "scope": "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018",
            "verdict_sha256": "e" * 64,
            "runtime": execution_runtime,
            "d018_transaction_sha256": sha256(paths["d018_tx"]),
        }
        write_json(paths["execution_gate"], execution_gate)
        set_metadata(paths["execution_gate"], 0, 1000, 0o640)

        control_sources = {
            adapter.PROJECT_ORIGINAL_CONTROLLER,
            paths["control"], paths["recovery_fact"],
            paths["recovery_verdict"], paths["work_package"],
        }
        frozen = {
            "schema_version":
                "m9-source-prepare-py39-uid1000-consumer-frozen-v1",
            "files": {path.as_posix(): sha256(path) for path in control_sources},
        }
        write_json(paths["frozen"], frozen)
        verdict = {
            "schema_version":
                "m9-source-prepare-py39-consumer-replacement-verdict-v1",
            "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT", "verdict": "PASS",
            "blocking": 0, "non_blocking": 0,
            "report_path": paths["consumer_report"].as_posix(),
            "report_sha256": sha256(paths["consumer_report"]),
            "work_package_path": paths["work_package"].as_posix(),
            "work_package_sha256": sha256(paths["work_package"]),
        }
        write_json(paths["consumer_verdict"], verdict)

        snapshot_sources = control_sources | {
            paths["frozen"], paths["consumer_verdict"], paths["consumer_report"]
        }
        entries: dict[str, object] = {}
        snapshot_members: dict[Path, Path] = {}
        for index, source in enumerate(sorted(snapshot_sources, key=lambda item: item.as_posix())):
            target = snapshot_controller if source == adapter.PROJECT_ORIGINAL_CONTROLLER else (
                snapshot_root / f"{index:02d}-{source.name}"
            )
            if target != snapshot_controller:
                target.write_bytes(source.read_bytes())
                set_metadata(target, 0, 1000, 0o440)
            snapshot_members[source] = target
            entries[source.as_posix()] = {
                "snapshot_path": target.as_posix(),
                "sha256": sha256(target), "bytes": target.stat().st_size,
            }
        snapshot_value = {
            "schema_version": "m9-source-prepare-py39-consumer-snapshot-v1",
            "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT",
            "issue_id": "M9-SP-PY39-B01", "files": entries,
        }
        write_json(snapshot_manifest, snapshot_value)
        set_metadata(snapshot_manifest, 0, 1000, 0o440)

        stack.enter_context(mock.patch.multiple(
            m9,
            STATE_PATH=paths["state"], OVERLAP_WORKFLOW_STATE=paths["workflow"],
            LEDGER_PATH=paths["ledger"], OVERLAP_TRANSACTION=paths["overlap_tx"],
            SOURCE_CONTROL_RECOVERY_TRANSACTION=paths["source_tx"],
            SOURCE_CONTROL_RECOVERY_GATE=paths["source_gate"],
            UNLIMITED_WALL_CLOCK_GATE=paths["d018_gate"],
            UNLIMITED_WALL_CLOCK_TRANSACTION=paths["d018_tx"],
            OVERLAP_AUDIT_GATE=paths["active_gate"],
            UNLIMITED_WALL_CLOCK_JOURNAL=paths["journal"],
            UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT=paths["pre_state_snapshot"],
            SOURCE_RECOVERY_PRODUCTS=tuple(),
        ))
        stack.enter_context(mock.patch.multiple(
            adapter,
            CONSUMER_GATE=paths["consumer_gate"], EXECUTION_GATE=paths["execution_gate"],
            CONSUMER_VERDICT=paths["consumer_verdict"],
            CONSUMER_REPORT=paths["consumer_report"],
            CONSUMER_WORK_PACKAGE=paths["work_package"],
            CONSUMER_FROZEN_HASHES=paths["frozen"],
            RECOVERY_FACT_REPORT=paths["recovery_fact"],
            RECOVERY_IMPLEMENTATION_VERDICT=paths["recovery_verdict"],
            SOURCE_PREPARE_AUTHORIZATION=paths["authorization"],
            SOURCE_PREPARE_AUTHORIZATION_RECORD=paths["authorization_record"],
            CONSUMER_CONTROL_FILES=control_sources,
            CONSUMER_SNAPSHOT_SOURCES=snapshot_sources,
        ))
        stack.__enter__()

        runtime = adapter.consumer_runtime_receipts()
        snapshot_receipt, _ = adapter.read_snapshot_manifest()
        historical = adapter.verify_historical_consumer_evidence()
        consumer_gate = {
            "schema_version": "m9-source-prepare-py39-uid1000-consumer-gate-v1",
            "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT", "status": "PASS",
            "blocking": 0, "non_blocking": 0,
            "scope": "ALLOW_ONE_SOURCE_PREPARE_AFTER_PY39_RECOVERY",
            "verdict_path": paths["consumer_verdict"].as_posix(),
            "verdict_sha256": sha256(snapshot_members[paths["consumer_verdict"]]),
            "frozen_hashes_path": paths["frozen"].as_posix(),
            "frozen_hashes_sha256": sha256(snapshot_members[paths["frozen"]]),
            "recovery_fact_report_path": paths["recovery_fact"].as_posix(),
            "recovery_fact_report_sha256": sha256(
                snapshot_members[paths["recovery_fact"]]
            ),
            "recovery_implementation_verdict_path": paths["recovery_verdict"].as_posix(),
            "recovery_implementation_verdict_sha256": sha256(
                snapshot_members[paths["recovery_verdict"]]
            ),
            "snapshot_manifest_path": snapshot_manifest.as_posix(),
            "snapshot_manifest_sha256": snapshot_receipt["sha256"],
            "historical_execution_gate_path": paths["execution_gate"].as_posix(),
            "historical_execution_gate_sha256": sha256(paths["execution_gate"]),
            "historical_execution_runtime_sha256": adapter.canonical_hash(
                execution_runtime
            ),
            "recovery_gate_sha256": adapter.EXPECTED_RECOVERY_GATE_SHA256,
            "recovery_transaction_sha256": adapter.EXPECTED_RECOVERY_TRANSACTION_SHA256,
            "historical_consumer_gate_path": historical_consumer_gate.as_posix(),
            "historical_consumer_gate_sha256": historical["consumer_gate"]["sha256"],
            "historical_bootstrap_receipt_path": historical_bootstrap_receipt.as_posix(),
            "historical_bootstrap_receipt_sha256": (
                historical["bootstrap_receipt"]["sha256"]
            ),
            "historical_snapshot_manifest_path": historical_snapshot_manifest.as_posix(),
            "historical_snapshot_manifest_sha256": (
                historical["snapshot_manifest"]["sha256"]
            ),
            "active_overlap_gate_sha256": runtime["active_overlap_gate_sha256"]["sha256"],
            "runtime": runtime,
        }
        write_json(paths["consumer_gate"], consumer_gate)
        set_metadata(paths["consumer_gate"], 0, 1000, 0o640)
        return stack, {
            "paths": paths, "m9": m9, "snapshot_root": snapshot_root,
            "snapshot_manifest": snapshot_manifest, "snapshot_members": snapshot_members,
            "historical_bootstrap_member": historical_bootstrap_member,
            "historical_snapshot_member": historical_snapshot_member,
        }

    def run_verifier_as_uid1000(self) -> tuple[int, str]:
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        if pid == 0:
            try:
                os.close(read_fd)
                os.setgroups([])
                os.setgid(1000)
                os.setuid(1000)
                result = adapter.verify_consumer_gate()
                os.write(write_fd, str(result["gate_receipt"]["sha256"]).encode())
                os._exit(0)
            except BaseException as exc:
                os.write(write_fd, repr(exc).encode())
                os._exit(1)
        os.close(write_fd)
        output = os.read(read_fd, 16384).decode()
        os.close(read_fd)
        _, status = os.waitpid(pid, 0)
        return os.waitstatus_to_exitcode(status), output

    def run_authorizer_as_uid1000(self) -> tuple[int, str]:
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        if pid == 0:
            try:
                os.close(read_fd)
                os.setgroups([]); os.setgid(1000); os.setuid(1000)
                result = adapter.verify_source_prepare_authorization(
                    source_prepare_argv()
                )
                os.write(write_fd, str(result["authorization_receipt"]["sha256"]).encode())
                os._exit(0)
            except BaseException as exc:
                os.write(write_fd, repr(exc).encode()); os._exit(1)
        os.close(write_fd)
        output = os.read(read_fd, 16384).decode(); os.close(read_fd)
        _, status = os.waitpid(pid, 0)
        return os.waitstatus_to_exitcode(status), output

    def test_original_launcher_control_freeze_is_unchanged(self) -> None:
        manifest = json.loads(
            (REPRODUCTION / "manifests/m9_overlap_py39_recovery_frozen_hashes.json").read_text(
                encoding="utf-8"
            )
        )
        files = manifest["files"]
        for path in (
            adapter.PROJECT_ORIGINAL_CONTROLLER,
            REPRODUCTION / "tests/test_m9_overlap_controls.py",
            REPRODUCTION / "configs/m9_overlap_only_contract.json",
            REPRODUCTION / "manifests/budget_contract.json",
        ):
            self.assertEqual(sha256(path), files[path.as_posix()])
        self.assertNotEqual(ADAPTER_PATH.parent, adapter.PROJECT_ORIGINAL_CONTROLLER.parent)

    def test_python39_frozen_manifest_is_the_common_runtime_authority(self) -> None:
        common = load_module(
            "m9_overlap_common_python39_tested",
            REPRODUCTION / "scripts/m9_overlap_common.py",
        )
        expected = REPRODUCTION / "manifests/m9_overlap_py39_recovery_frozen_hashes.json"
        self.assertEqual(common.FROZEN_HASHES_PATH, expected)
        contract, _ = common.load_contract()
        self.assertEqual(
            contract["runtime_paths"]["project_frozen_hashes"], expected.as_posix()
        )
        budget_text = adapter.PROJECT_ORIGINAL_CONTROLLER.read_text(encoding="utf-8")
        launcher_text = (REPRODUCTION / "scripts/m9_overlap_source_launcher.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("m9_overlap_py39_recovery_frozen_hashes.json", budget_text)
        self.assertIn("m9_overlap_py39_recovery_frozen_hashes.json", launcher_text)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); work = root / "work.md"; report = root / "report.md"
            gate_path = root / "gate.json"
            work.write_text("work\n", encoding="utf-8")
            report.write_text("PASS\n", encoding="utf-8")
            gate = {
                "schema_version": "m9-overlap-audit-gate-v1", "status": "PASS",
                "blocking": 0, "non_blocking": 0,
                "work_package_path": work.as_posix(), "work_package_sha256": sha256(work),
                "audit_report_path": report.as_posix(), "audit_report_sha256": sha256(report),
                "frozen_hashes_sha256": sha256(expected),
            }
            write_json(gate_path, gate)
            contract = json.loads(json.dumps(contract))
            contract["runtime_paths"]["audit_gate"] = gate_path.as_posix()
            self.assertEqual(common.verify_frozen_project_files(contract), gate)

    def test_adapter_rejects_every_action_except_source_prepare(self) -> None:
        project_m9 = load_module(
            "m9_budget_adapter_action_parser",
            adapter.PROJECT_ORIGINAL_CONTROLLER,
        )
        source_build = source_prepare_argv()
        source_build[source_build.index("source_prepare")] = "source_build"
        duplicate_operation_id = source_prepare_argv() + [
            "--consumer-operation-id", "b" * 32
        ]
        with mock.patch.object(adapter, "_M9", project_m9):
            for argv in (
                [], ["status"], ["run"],
                source_build,
                source_prepare_argv() + ["--"],
                duplicate_operation_id,
                source_prepare_argv("A" * 32),
                [item for item in source_prepare_argv() if item != "--overlap-operation"],
            ):
                with self.subTest(argv=argv), self.assertRaises(SystemExit):
                    adapter.require_source_prepare_argv(argv)
            self.assertEqual(
                adapter.require_source_prepare_argv(source_prepare_argv()),
                OPERATION_ID,
            )

    def test_adapter_bridges_to_the_real_frozen_parser_without_free_argv(self) -> None:
        project_m9 = load_module(
            "m9_budget_adapter_bridge_parser",
            adapter.PROJECT_ORIGINAL_CONTROLLER,
        )
        with mock.patch.object(adapter, "_M9", project_m9):
            operation_id, delegated = adapter.source_prepare_adapter_argv(
                source_prepare_argv()
            )
        self.assertEqual(operation_id, OPERATION_ID)
        self.assertNotIn("--consumer-operation-id", delegated)
        m9 = project_m9
        parsed = m9.build_parser().parse_args(delegated)
        self.assertTrue(parsed.overlap_operation)
        self.assertEqual(parsed.overlap_action, "source_prepare")
        self.assertEqual(parsed.command, [])
        self.assertEqual(parsed.bucket, "none")
        self.assertEqual(parsed.cpu_bucket, "overlap_build")
        workflow = {
            "stage": "AUDIT_PASSED",
            "hard_stopped": False,
            "apt_install_completed": True,
            "next_structure_id": None,
            "active_structure_id": None,
        }
        self.assertEqual(
            m9.validate_overlap_request(parsed, workflow),
            ("source_prepare", "overlap_build", 1073741824),
        )

    def test_work_package_single_fd_loader_accepts_only_exact_bytes(self) -> None:
        work_package = (
            TEST_PATH.parents[2]
            / "08_audits/M9_source_prepare_py39_consumer_replacement_work_package.md"
        )
        text = work_package.read_text(encoding="utf-8")
        loader = text.split("```python\n", 1)[1].split("\n```", 1)[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = root / "marker"
            payload = (
                "from pathlib import Path\n"
                "import sys\n"
                "Path(sys.argv[-1]).write_text('trusted', encoding='utf-8')\n"
            ).encode()
            script = root / "payload.py"
            script.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            command = [
                sys.executable, "-I", "-S", "-B", "-c", loader,
                script.as_posix(), digest, marker.as_posix(),
            ]
            accepted = subprocess.run(command, capture_output=True, check=False)
            self.assertEqual(accepted.returncode, 0, accepted.stderr.decode())
            self.assertEqual(marker.read_text(encoding="utf-8"), "trusted")
            marker.unlink()
            rejected = subprocess.run(
                [*command[:7], "0" * 64, marker.as_posix()],
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse(marker.exists())

    def test_project_side_adapter_cannot_be_the_formal_entrypoint(self) -> None:
        argv = [ADAPTER_PATH.as_posix(), *source_prepare_argv()]
        with mock.patch.object(sys, "argv", argv), self.assertRaises(SystemExit):
            adapter.main()

    def test_project_side_installer_cannot_be_the_formal_entrypoint(self) -> None:
        installer = load_module("m9_uid1000_consumer_installer_rejected", INSTALLER_PATH)
        with mock.patch.object(installer, "FROZEN_PYTHON", Path(sys.executable)):
            with self.assertRaises(SystemExit):
                installer.main()
        direct = subprocess.run(
            [sys.executable, "-I", "-S", "-B", INSTALLER_PATH.as_posix()],
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(direct.returncode, 0)
        self.assertIn(b"trusted bootstrap", direct.stderr)
        source_lines = INSTALLER_PATH.read_text(encoding="utf-8").splitlines()
        adapter_line = next(
            index for index, line in enumerate(source_lines, start=1)
            if line.startswith("ADAPTER_IMPORT =")
        )
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "adapter-top-level-marker"
            probe = """
import runpy
import sys
from pathlib import Path

target = Path(sys.argv[1]).resolve(strict=True)
marker = Path(sys.argv[2])
adapter_line = int(sys.argv[3])

def trace(frame, event, argument):
    if (
        event == "line"
        and Path(frame.f_code.co_filename).resolve(strict=False) == target
        and frame.f_lineno >= adapter_line
    ):
        marker.write_text("ADAPTER_EXECUTED", encoding="utf-8")
    return trace

sys.settrace(trace)
runpy.run_path(target.as_posix(), run_name="__main__")
"""
            traced = subprocess.run(
                [
                    sys.executable, "-I", "-S", "-B", "-c", probe,
                    INSTALLER_PATH.as_posix(), marker.as_posix(), str(adapter_line),
                ],
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(traced.returncode, 0)
            self.assertIn(b"trusted bootstrap", traced.stderr)
            self.assertFalse(marker.exists())

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_real_uid1000_verifies_without_root_private_reads(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, fixture = self.fixture(Path(temporary))
            with stack:
                code, output = self.run_verifier_as_uid1000()
                self.assertEqual(code, 0, output)
                self.assertEqual(output, sha256(fixture["paths"]["consumer_gate"]))

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_source_prepare_requires_separate_exact_single_run_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, fixture = self.fixture(Path(temporary))
            paths = fixture["paths"]
            with stack:
                self.assertNotEqual(self.run_authorizer_as_uid1000()[0], 0)
                paths["authorization_record"].write_text(
                    "fresh user authorization fixture\n", encoding="utf-8"
                )
                set_metadata(paths["authorization_record"], 0, 1000, 0o440)
                consumer_gate = json.loads(paths["consumer_gate"].read_text(encoding="utf-8"))
                authorization = {
                    "schema_version": "m9-source-prepare-py39-single-run-authorization-v1",
                    "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT",
                    "status": "AUTHORIZED",
                    "scope": "ALLOW_EXACTLY_ONE_SOURCE_PREPARE",
                    "action": "source_prepare",
                    "operation_id": OPERATION_ID,
                    "authorization_nonce": "b" * 64,
                    "authorization_record_path": paths["authorization_record"].as_posix(),
                    "authorization_record_sha256": sha256(paths["authorization_record"]),
                    "consumer_gate_sha256": sha256(paths["consumer_gate"]),
                    "active_overlap_gate_sha256": consumer_gate["active_overlap_gate_sha256"],
                    "runtime_sha256": adapter.canonical_hash(consumer_gate["runtime"]),
                }
                write_json(paths["authorization"], authorization)
                set_metadata(paths["authorization"], 0, 1000, 0o640)
                self.assertEqual(self.run_authorizer_as_uid1000()[0], 0)
                authorization["action"] = "source_build"
                write_json(paths["authorization"], authorization)
                set_metadata(paths["authorization"], 0, 1000, 0o640)
                self.assertNotEqual(self.run_authorizer_as_uid1000()[0], 0)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_runtime_bytes_and_metadata_are_both_sealed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, fixture = self.fixture(Path(temporary))
            paths = fixture["paths"]
            with stack:
                original = paths["state"].read_bytes()
                paths["state"].write_bytes(original + b" ")
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)
                paths["state"].write_bytes(original)
                set_metadata(paths["state"], 1000, 1000, 0o666)
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)
                set_metadata(paths["state"], 1000, 1000, 0o644)
                set_metadata(paths["d018_tx"], 1000, 1000, 0o640)
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_snapshot_metadata_and_links_are_sealed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, fixture = self.fixture(Path(temporary))
            with stack:
                member = fixture["snapshot_members"][fixture["paths"]["control"]]
                link = Path(temporary) / "extra-link"
                os.link(member, link)
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)
                link.unlink()
                set_metadata(member, 0, 1000, 0o640)
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_historical_consumer_bytes_and_closed_sets_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, fixture = self.fixture(Path(temporary))
            member = fixture["historical_bootstrap_member"]
            with stack:
                original = member.read_bytes()
                member.write_bytes(original + b"# drift\n")
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)
                member.write_bytes(original)
                set_metadata(member, 0, 1000, 0o440)
                extra = member.parent / "unexpected"
                extra.write_bytes(b"unexpected")
                set_metadata(extra, 0, 1000, 0o440)
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_dangling_source_product_is_present_and_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, fixture = self.fixture(Path(temporary))
            product = Path(temporary) / "dangling-product"
            with stack, mock.patch.object(
                fixture["m9"], "SOURCE_RECOVERY_PRODUCTS", (product,)
            ):
                product.symlink_to(Path(temporary) / "missing-target")
                self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_cross_read_runtime_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, fixture = self.fixture(Path(temporary))
            state_path = fixture["paths"]["state"]
            with stack:
                original_function = adapter.consumer_runtime_snapshot
                original_payload = state_path.read_bytes()
                calls = 0

                def mutate_after_first_snapshot():
                    nonlocal calls
                    result = original_function()
                    calls += 1
                    if calls == 1:
                        state_path.write_bytes(original_payload + b" ")
                    return result

                with mock.patch.object(
                    adapter, "consumer_runtime_snapshot", side_effect=mutate_after_first_snapshot
                ):
                    self.assertNotEqual(self.run_verifier_as_uid1000()[0], 0)
                state_path.write_bytes(original_payload)

    def test_main_revalidates_at_first_state_write(self) -> None:
        m9 = mock.Mock()
        adapter._M9 = m9
        parser_m9 = load_module(
            "m9_budget_adapter_main_parser",
            adapter.PROJECT_ORIGINAL_CONTROLLER,
        )
        m9.build_parser = parser_m9.build_parser
        verified = {"execution_gate": {"runtime": {"sealed": True}}}
        writes: list[str] = []

        def atomic_json(path: Path, value: dict) -> None:
            writes.append(path.name)

        def delegated_main() -> int:
            m9.verify_unlimited_wall_clock_execution_ready()
            m9.verify_unlimited_wall_clock_execution_fact_gate()
            m9.d018_execution_runtime_receipts()
            m9.atomic_json(Path("state.json"), {})
            m9.atomic_json(Path("workflow.json"), {})
            return 0

        m9.atomic_json = atomic_json
        m9.main = delegated_main
        argv = [ADAPTER_PATH.as_posix(), *source_prepare_argv()]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            adapter, "INSTALLED_ADAPTER", ADAPTER_PATH
        ), mock.patch.object(
            adapter, "verify_source_prepare_authorization", return_value=verified
        ) as verifier:
            self.assertEqual(adapter.main(), 0)
        self.assertEqual(verifier.call_count, 5)
        self.assertEqual(writes, ["state.json", "workflow.json"])
        adapter._M9 = None

    def test_main_missing_authorization_is_zero_write_rejected(self) -> None:
        m9 = mock.Mock(); adapter._M9 = m9
        original_atomic_json = m9.atomic_json
        argv = [ADAPTER_PATH.as_posix(), *source_prepare_argv()]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            adapter, "INSTALLED_ADAPTER", ADAPTER_PATH
        ), mock.patch.object(
            adapter, "verify_source_prepare_authorization",
            side_effect=SystemExit("authorization missing"),
        ):
            with self.assertRaises(SystemExit):
                adapter.main()
        m9.main.assert_not_called(); original_atomic_json.assert_not_called()
        adapter._M9 = None

    def test_installer_checks_full_history_and_authorization_before_snapshot_write(self) -> None:
        installer = load_module("m9_uid1000_consumer_installer_order", INSTALLER_PATH)
        historical = {"sealed": True}
        events: list[str] = []

        def verify_history() -> dict[str, object]:
            events.append("history")
            return historical

        def authorization_absent(path: object) -> bool:
            self.assertEqual(Path(path), installer.consumer.SOURCE_PREPARE_AUTHORIZATION)
            events.append("authorization")
            return False

        def prepare(payloads: object, lock_handle: object) -> tuple[dict, dict]:
            events.append("prepare_snapshot")
            return {"core": True}, {"snapshot": True}

        with mock.patch.object(
            installer.consumer,
            "verify_historical_consumer_evidence",
            side_effect=verify_history,
        ), mock.patch.object(
            installer.os.path, "lexists", side_effect=authorization_absent
        ), mock.patch.object(
            installer, "prepare_snapshot_for_refresh", side_effect=prepare
        ), mock.patch.object(
            installer, "verify_installation_preflight"
        ), mock.patch.object(
            installer, "refresh_active_overlap_gate", return_value={"refresh": True}
        ), mock.patch.object(
            installer, "build_consumer_gate", return_value={"gate": True}
        ), mock.patch.object(
            installer, "install_consumer_gate", return_value={"receipt": True}
        ):
            receipt = installer.install_under_lock({}, historical, object())
        self.assertEqual(receipt, {"receipt": True})
        self.assertEqual(events[:3], ["history", "authorization", "prepare_snapshot"])

        for scenario in ("history_drift", "authorization_present"):
            with self.subTest(scenario=scenario):
                prepare_mock = mock.Mock()
                history_value = {"drift": True} if scenario == "history_drift" else historical
                authorization_value = scenario == "authorization_present"
                with mock.patch.object(
                    installer.consumer,
                    "verify_historical_consumer_evidence",
                    return_value=history_value,
                ), mock.patch.object(
                    installer.os.path,
                    "lexists",
                    return_value=authorization_value,
                ), mock.patch.object(
                    installer, "prepare_snapshot_for_refresh", prepare_mock
                ), self.assertRaises(SystemExit):
                    installer.install_under_lock({}, historical, object())
                prepare_mock.assert_not_called()

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_installer_creates_single_link_root_snapshot_idempotently(self) -> None:
        installer = load_module("m9_uid1000_consumer_installer_tested", INSTALLER_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chown(root, 0, 1000)
            os.chmod(root, 0o750)
            snapshot_root = root / "snapshot"
            manifest_path = snapshot_root / "snapshot_manifest.json"
            staging = root / "snapshot.staging"
            source = root / "source.txt"
            source.write_text("sealed\n", encoding="utf-8")
            payloads = {source: source.read_bytes()}
            with mock.patch.multiple(
                installer.consumer,
                SNAPSHOT_ROOT=snapshot_root,
                SNAPSHOT_MANIFEST=manifest_path,
            ), mock.patch.object(installer, "STAGING_ROOT", staging):
                first = installer.install_snapshot(payloads)
                second = installer.install_snapshot(payloads)
            self.assertEqual(first, second)
            self.assertEqual(snapshot_root.stat().st_mode & 0o777, 0o550)
            entry = first["manifest"]["files"][source.as_posix()]
            member = Path(entry["snapshot_path"])
            member_stat = member.stat()
            self.assertEqual((member_stat.st_uid, member_stat.st_gid), (0, 1000))
            self.assertEqual(member_stat.st_mode & 0o777, 0o440)
            self.assertEqual(member_stat.st_nlink, 1)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_installer_resumes_sealed_staging_after_rename_failure(self) -> None:
        installer = load_module("m9_uid1000_consumer_installer_resume", INSTALLER_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chown(root, 0, 1000)
            os.chmod(root, 0o750)
            snapshot_root = root / "snapshot"
            manifest_path = snapshot_root / "snapshot_manifest.json"
            staging = root / "snapshot.staging"
            source = root / "source.txt"
            source.write_text("sealed\n", encoding="utf-8")
            payloads = {source: source.read_bytes()}
            real_replace = installer.os.replace
            failed = False

            def fail_final_rename_once(old: object, new: object) -> None:
                nonlocal failed
                if Path(old) == staging and Path(new) == snapshot_root and not failed:
                    failed = True
                    raise OSError("simulated rename failure")
                real_replace(old, new)

            with mock.patch.multiple(
                installer.consumer,
                SNAPSHOT_ROOT=snapshot_root,
                SNAPSHOT_MANIFEST=manifest_path,
            ), mock.patch.object(installer, "STAGING_ROOT", staging):
                with mock.patch.object(installer.os, "replace", side_effect=fail_final_rename_once):
                    with self.assertRaises(OSError):
                        installer.install_snapshot(payloads)
                self.assertEqual(staging.stat().st_mode & 0o777, 0o550)
                installed = installer.install_snapshot(payloads)
            self.assertEqual(
                installed["manifest"]["files"][source.as_posix()]["sha256"],
                hashlib.sha256(payloads[source]).hexdigest(),
            )

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_installer_top_level_resumes_both_rename_windows_and_terminal_gate_gap(self) -> None:
        for failure_point in ("retire", "activate"):
            with self.subTest(failure_point=failure_point), tempfile.TemporaryDirectory() as temporary:
                installer = load_module(
                    f"m9_uid1000_consumer_refresh_{failure_point}", INSTALLER_PATH
                )
                root = Path(temporary)
                manifests = root / "manifests"
                control = root / "control"
                manifests.mkdir(); control.mkdir()
                active = manifests / "active.json"
                retired = manifests / "retired.json"
                staging = manifests / "staging.json"
                journal = control / "journal.json"
                lock = manifests / "budget.lock"
                snapshot_root = root / "snapshot"
                snapshot_root.mkdir()
                lock.write_bytes(b"")
                set_metadata(lock, 1000, 1000, 0o644)
                old_payload = b'{"gate":"old"}\n'
                new_gate = {"gate": "new"}
                new_payload = (
                    json.dumps(new_gate, ensure_ascii=False, indent=2) + "\n"
                ).encode()
                active.write_bytes(old_payload)
                set_metadata(active, 0, 1000, 0o640)
                active_stat = active.stat()
                recovered_core = {
                    "pre_replacement_active_gate": {
                        "path": active.as_posix(), "bytes": len(old_payload),
                        "sha256": hashlib.sha256(old_payload).hexdigest(),
                        "uid": 0, "gid": 1000, "mode": 0o640, "nlink": 1,
                        "st_dev": active_stat.st_dev, "st_ino": active_stat.st_ino,
                    }
                }

                def read_gate(path: Path) -> tuple[dict[str, object], dict, bytes]:
                    payload = path.read_bytes()
                    observed = path.stat()
                    if (
                        observed.st_uid != 0
                        or observed.st_gid != 1000
                        or observed.st_mode & 0o777 != 0o640
                        or observed.st_nlink != 1
                    ):
                        raise SystemExit("fixture gate metadata mismatch")
                    return ({
                        "path": path.as_posix(), "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "uid": 0, "gid": 1000, "mode": 0o640, "nlink": 1,
                    }, json.loads(payload), payload)

                def read_inode(path: Path) -> tuple[dict[str, object], bytes]:
                    payload = path.read_bytes(); observed = path.stat()
                    return ({
                        "path": path.as_posix(), "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "uid": observed.st_uid, "gid": observed.st_gid,
                        "mode": observed.st_mode & 0o777, "nlink": observed.st_nlink,
                        "dev": observed.st_dev, "ino": observed.st_ino,
                    }, payload)

                def rename_inode(active_path: Path, retired_path: Path,
                                  expected: dict[str, object]) -> dict[str, object]:
                    before, _ = read_inode(active_path)
                    if before != expected:
                        raise SystemExit("fixture active inode drift")
                    installer.os.replace(active_path, retired_path)
                    after, _ = read_inode(retired_path)
                    if after != dict(expected, path=retired_path.as_posix()):
                        raise SystemExit("fixture retired inode drift")
                    return after

                def atomic_owned(path: Path, payload: bytes, **_: object) -> None:
                    if path.exists():
                        if path.read_bytes() != payload:
                            raise SystemExit("fixture atomic target differs")
                        return
                    path.write_bytes(payload); set_metadata(path, 0, 1000, 0o640)

                def read_private(path: Path) -> tuple[dict[str, object], bytes]:
                    payload = path.read_bytes(); observed = path.stat()
                    return ({
                        "path": path.as_posix(), "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "uid": observed.st_uid, "gid": observed.st_gid,
                        "mode": observed.st_mode & 0o777, "nlink": observed.st_nlink,
                    }, payload)

                def atomic_private(path: Path, value: dict) -> None:
                    write_json(path, value); set_metadata(path, 0, 0, 0o600)

                fake_m9 = mock.Mock(
                    OVERLAP_AUDIT_GATE=active,
                    LOCK_PATH=lock,
                    read_d018_control_json=read_gate,
                    read_d018_inode_regular_bytes=read_inode,
                    rename_d018_gate_preserving_inode=rename_inode,
                    atomic_owned_durable_bytes=atomic_owned,
                    read_strict_root_private_bytes=read_private,
                    atomic_root_private_json=atomic_private,
                )
                real_replace = installer.os.replace
                failed = False

                def fail_once(old: object, new: object) -> None:
                    nonlocal failed
                    old_path, new_path = Path(old), Path(new)
                    target = (
                        old_path == active and new_path == retired
                        if failure_point == "retire"
                        else old_path == staging and new_path == active
                    )
                    if target and not failed:
                        failed = True
                        real_replace(old, new)
                        raise OSError("simulated active-gate rename failure")
                    real_replace(old, new)

                with lock.open("r+") as lock_handle, mock.patch.object(
                    installer.consumer, "original_controller", return_value=fake_m9
                ), mock.patch.object(
                    installer, "replacement_active_gate", return_value=new_gate
                ), mock.patch.object(
                    installer, "verify_recovered_core", return_value=recovered_core
                ), mock.patch.object(
                    installer, "install_snapshot", return_value={}
                ), mock.patch.object(
                    installer.consumer, "SNAPSHOT_ROOT", snapshot_root
                ), mock.patch.multiple(
                    installer,
                    REFRESH_JOURNAL=journal,
                    ACTIVE_GATE_RETIRED=retired,
                    ACTIVE_GATE_STAGING=staging,
                    PRE_REPLACEMENT_ACTIVE_GATE_SHA256=hashlib.sha256(old_payload).hexdigest(),
                ), mock.patch.object(
                    installer.os, "replace", side_effect=fail_once
                ):
                    with self.assertRaisesRegex(
                        OSError, "simulated active-gate rename failure"
                    ):
                        installer.refresh_active_overlap_gate({}, lock_handle)
                    resumed_core, resumed_snapshot = (
                        installer.prepare_snapshot_for_refresh({}, lock_handle)
                    )
                    self.assertEqual(resumed_core, recovered_core)
                    first = installer.refresh_active_overlap_gate(
                        resumed_snapshot, lock_handle
                    )
                    terminal_core, terminal_snapshot = (
                        installer.prepare_snapshot_for_refresh({}, lock_handle)
                    )
                    self.assertEqual(terminal_core, recovered_core)
                    second = installer.refresh_active_overlap_gate(
                        terminal_snapshot, lock_handle
                    )
                self.assertEqual(first, second)
                self.assertEqual(active.read_bytes(), new_payload)
                self.assertEqual(retired.read_bytes(), old_payload)
                self.assertFalse(staging.exists())
                self.assertEqual(
                    json.loads(journal.read_text(encoding="utf-8"))["state"],
                    "SUCCESS_COMMITTED",
                )

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_refresh_rejects_illegal_phase_and_same_byte_inode_swap(self) -> None:
        for scenario in ("prepared_retired", "staged_inode_swap"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                installer = load_module(f"m9_refresh_reject_{scenario}", INSTALLER_PATH)
                root = Path(temporary); manifests = root / "manifests"; control = root / "control"
                manifests.mkdir(); control.mkdir()
                active = manifests / "active.json"; retired = manifests / "retired.json"
                staging = manifests / "staging.json"; journal = control / "journal.json"
                lock = manifests / "budget.lock"; lock.write_bytes(b"")
                set_metadata(lock, 1000, 1000, 0o644)
                old_payload = b'{"gate":"old"}\n'; new_gate = {"gate": "new"}
                new_payload = (json.dumps(new_gate, ensure_ascii=False, indent=2) + "\n").encode()
                active.write_bytes(old_payload); set_metadata(active, 0, 1000, 0o640)
                staging.write_bytes(new_payload); set_metadata(staging, 0, 1000, 0o640)
                m9 = load_module(
                    f"m9_refresh_budget_{scenario}", adapter.PROJECT_ORIGINAL_CONTROLLER
                )
                with mock.patch.multiple(m9, OVERLAP_AUDIT_GATE=active, LOCK_PATH=lock), \
                     mock.patch.object(installer.consumer, "original_controller", return_value=m9), \
                     mock.patch.object(installer, "replacement_active_gate", return_value=new_gate), \
                     mock.patch.multiple(
                         installer, REFRESH_JOURNAL=journal, ACTIVE_GATE_RETIRED=retired,
                         ACTIVE_GATE_STAGING=staging,
                         PRE_REPLACEMENT_ACTIVE_GATE_SHA256=hashlib.sha256(old_payload).hexdigest(),
                     ):
                    with lock.open("r+") as lock_handle:
                        old_receipt, _ = m9.read_d018_inode_regular_bytes(active)
                        staged_receipt, _ = m9.read_d018_inode_regular_bytes(staging)
                        recovered_core = {
                            "pre_replacement_active_gate": {
                                **{
                                    key: value for key, value in old_receipt.items()
                                    if key not in {"dev", "ino"}
                                },
                                "st_dev": old_receipt["dev"],
                                "st_ino": old_receipt["ino"],
                            }
                        }
                        base = {
                            "schema_version": "m9-source-prepare-py39-consumer-refresh-v1",
                            "decision_id": "D-018-PY39-CONSUMER-REPLACEMENT",
                            "old_active": old_receipt,
                            "old_active_sha256": hashlib.sha256(old_payload).hexdigest(),
                            "new_active_sha256": hashlib.sha256(new_payload).hexdigest(),
                            "retired_path": retired.as_posix(),
                            "staging_path": staging.as_posix(),
                            "budget_lock": installer.verify_budget_lock(lock_handle),
                        }
                        if scenario == "prepared_retired":
                            os.replace(active, retired)
                            value = dict(base, state="PREPARED")
                        else:
                            value = dict(base, state="STAGED", staging=staged_receipt)
                            replacement = manifests / "replacement.json"
                            replacement.write_bytes(old_payload)
                            set_metadata(replacement, 0, 1000, 0o640)
                            os.replace(replacement, active)
                        write_json(journal, value); set_metadata(journal, 0, 0, 0o600)
                        before = journal.read_bytes()
                        with mock.patch.object(
                            installer,
                            "verify_recovered_core",
                            return_value=recovered_core,
                        ), self.assertRaises(SystemExit):
                            installer.refresh_active_overlap_gate({}, lock_handle)
                        self.assertEqual(journal.read_bytes(), before)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_consumer_gate_dangling_symlink_is_zero_write_rejected(self) -> None:
        installer = load_module("m9_consumer_gate_symlink", INSTALLER_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            gate = Path(temporary) / "consumer-gate.json"
            gate.symlink_to(Path(temporary) / "missing-target")
            fake_m9 = mock.Mock()
            fake_m9.read_d018_control_json.side_effect = SystemExit("symlink rejected")
            with mock.patch.object(installer.consumer, "CONSUMER_GATE", gate), \
                 mock.patch.object(installer.consumer, "original_controller", return_value=fake_m9):
                with self.assertRaises(SystemExit):
                    installer.install_consumer_gate({"sealed": True})
            self.assertTrue(os.path.lexists(gate)); self.assertTrue(gate.is_symlink())
            fake_m9.atomic_owned_durable_bytes.assert_not_called()

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_bootstrap_installs_exact_root_owned_trust_set(self) -> None:
        bootstrap = load_module("m9_uid1000_consumer_bootstrap_tested", BOOTSTRAP_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.chown(root, 0, 1000)
            os.chmod(root, 0o750)
            trusted = root / "bootstrap"
            staging = root / "bootstrap.staging"
            sources = {
                "bootstrap": root / "project-bootstrap.py",
                "installer": root / "project-installer.py",
                "adapter": root / "project-adapter.py",
                "verdict": root / "consumer-verdict.json",
                "report": root / "consumer-report.md",
            }
            for name, path in sources.items():
                path.write_text(f"# {name}\n", encoding="utf-8")
            frozen_path = root / "frozen.json"
            lock_path = root / "budget.lock"
            lock_path.write_bytes(b"")
            set_metadata(lock_path, 1000, 1000, 0o644)
            files = {path.as_posix(): sha256(path) for path in sources.values()}
            write_json(frozen_path, {"files": files})
            hashes = [
                sha256(sources[name])
                for name in ("bootstrap", "installer", "adapter")
            ]
            frozen_sha = sha256(frozen_path)
            real_replace = bootstrap.os.replace
            failed = False

            def fail_bootstrap_rename_once(old: object, new: object) -> None:
                nonlocal failed
                if Path(old) == staging and Path(new) == trusted and not failed:
                    failed = True
                    raise OSError("simulated bootstrap rename failure")
                real_replace(old, new)

            with mock.patch.multiple(
                bootstrap,
                PROJECT_BOOTSTRAP=sources["bootstrap"],
                PROJECT_INSTALLER=sources["installer"],
                PROJECT_ADAPTER=sources["adapter"],
                PROJECT_VERDICT=sources["verdict"],
                PROJECT_REPORT=sources["report"],
                FROZEN_HASHES=frozen_path,
                TRUSTED_ROOT=trusted,
                STAGING_ROOT=staging,
                TRUSTED_BOOTSTRAP=trusted / "m9_uid1000_consumer_bootstrap.py",
                TRUSTED_INSTALLER=trusted / "m9_uid1000_consumer_install.py",
                TRUSTED_ADAPTER=trusted / "m9_budget_uid1000_consumer.py",
                TRUSTED_VERDICT=trusted / "consumer-verdict.json",
                TRUSTED_REPORT=trusted / "consumer-report.md",
                TRUSTED_RECEIPT=trusted / "bootstrap_receipt.json",
                FROZEN_PYTHON=Path(sys.executable),
                LOCK_PATH=lock_path,
            ), mock.patch.object(
                sys,
                "argv",
                [
                    BOOTSTRAP_PATH.as_posix(), *hashes, frozen_sha,
                    sha256(sources["verdict"]), sha256(sources["report"]),
                ],
            ), mock.patch.object(
                bootstrap, "verify_bootstrap_runtime", return_value={"sealed": True}
            ):
                with mock.patch.object(
                    bootstrap.os, "replace", side_effect=fail_bootstrap_rename_once
                ):
                    with self.assertRaisesRegex(OSError, "simulated bootstrap rename failure"):
                        bootstrap.main()
                self.assertEqual(staging.stat().st_mode & 0o777, 0o550)
                self.assertEqual(bootstrap.main(), 0)
                self.assertEqual(bootstrap.main(), 0)
            self.assertEqual(trusted.stat().st_mode & 0o777, 0o550)
            self.assertEqual(
                {path.name for path in trusted.iterdir()},
                {
                    "m9_uid1000_consumer_bootstrap.py",
                    "m9_uid1000_consumer_install.py",
                    "m9_budget_uid1000_consumer.py",
                    "consumer-verdict.json",
                    "consumer-report.md",
                    "bootstrap_receipt.json",
                },
            )
            for member in trusted.iterdir():
                observed = member.stat()
                self.assertEqual((observed.st_uid, observed.st_gid), (0, 1000))
                self.assertEqual(observed.st_mode & 0o777, 0o440)
                self.assertEqual(observed.st_nlink, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
