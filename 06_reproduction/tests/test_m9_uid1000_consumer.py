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

        names = (
            "state", "workflow", "ledger", "overlap_tx", "source_tx",
            "source_gate", "d018_gate", "d018_tx", "execution_gate",
            "active_gate", "consumer_gate", "consumer_verdict", "frozen",
            "authorization", "work_package", "consumer_report", "journal",
            "pre_state_snapshot", "control",
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
        paths["authorization"].write_text("authorized\n", encoding="utf-8")
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
            paths["control"], paths["authorization"], paths["work_package"],
        }
        frozen = {
            "schema_version":
                "m9-unlimited-wall-clock-uid1000-consumer-frozen-hashes-v1",
            "files": {path.as_posix(): sha256(path) for path in control_sources},
        }
        write_json(paths["frozen"], frozen)
        verdict = {
            "schema_version":
                "m9-unlimited-wall-clock-uid1000-consumer-audit-verdict-v1",
            "decision_id": "D-018", "verdict": "PASS",
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
            "schema_version": "m9-uid1000-consumer-snapshot-v1",
            "decision_id": "D-018", "issue_id": "D018-EGF-B01", "files": entries,
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
            AUTHORIZATION=paths["authorization"],
            CONSUMER_CONTROL_FILES=control_sources,
            CONSUMER_SNAPSHOT_SOURCES=snapshot_sources,
        ))
        stack.__enter__()

        runtime = adapter.consumer_runtime_receipts()
        snapshot_receipt, _ = adapter.read_snapshot_manifest()
        consumer_gate = {
            "schema_version": "m9-unlimited-wall-clock-uid1000-consumer-gate-v1",
            "decision_id": "D-018", "status": "PASS",
            "blocking": 0, "non_blocking": 0,
            "scope": "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018",
            "verdict_path": paths["consumer_verdict"].as_posix(),
            "verdict_sha256": sha256(snapshot_members[paths["consumer_verdict"]]),
            "frozen_hashes_path": paths["frozen"].as_posix(),
            "frozen_hashes_sha256": sha256(snapshot_members[paths["frozen"]]),
            "authorization_path": paths["authorization"].as_posix(),
            "authorization_sha256": sha256(snapshot_members[paths["authorization"]]),
            "snapshot_manifest_path": snapshot_manifest.as_posix(),
            "snapshot_manifest_sha256": snapshot_receipt["sha256"],
            "execution_gate_path": paths["execution_gate"].as_posix(),
            "execution_gate_sha256": sha256(paths["execution_gate"]),
            "sealed_execution_runtime_sha256": adapter.canonical_hash(execution_runtime),
            "d018_transaction_sha256": sha256(paths["d018_tx"]),
            "runtime": runtime,
        }
        write_json(paths["consumer_gate"], consumer_gate)
        set_metadata(paths["consumer_gate"], 0, 1000, 0o640)
        return stack, {
            "paths": paths, "m9": m9, "snapshot_root": snapshot_root,
            "snapshot_manifest": snapshot_manifest, "snapshot_members": snapshot_members,
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

    def test_original_launcher_control_freeze_is_unchanged(self) -> None:
        manifest = json.loads(
            (REPRODUCTION / "manifests/m9_overlap_frozen_hashes.json").read_text(
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

    def test_adapter_rejects_every_action_except_source_prepare(self) -> None:
        for argv in (
            [], ["status"], ["run"],
            ["run", "--overlap-operation", "--overlap-action", "source_build"],
            ["run", "--overlap-operation", "--overlap-action", "source_prepare", "--"],
        ):
            with self.subTest(argv=argv), self.assertRaises(SystemExit):
                adapter.require_source_prepare_argv(argv)
        adapter.require_source_prepare_argv(
            ["run", "--overlap-operation", "--overlap-action", "source_prepare"]
        )

    def test_work_package_single_fd_loader_accepts_only_exact_bytes(self) -> None:
        work_package = (
            TEST_PATH.parents[2]
            / "08_audits/M9_unlimited_wall_clock_uid1000_consumer_work_package.md"
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
        argv = [
            ADAPTER_PATH.as_posix(), "run", "--overlap-operation",
            "--overlap-action", "source_prepare",
        ]
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
        argv = [
            ADAPTER_PATH.as_posix(), "run", "--overlap-operation",
            "--overlap-action", "source_prepare",
        ]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            adapter, "INSTALLED_ADAPTER", ADAPTER_PATH
        ), mock.patch.object(
            adapter, "verify_consumer_gate", return_value=verified
        ) as verifier:
            self.assertEqual(adapter.main(), 0)
        self.assertEqual(verifier.call_count, 4)
        self.assertEqual(writes, ["state.json", "workflow.json"])
        adapter._M9 = None

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
            ), mock.patch.object(
                sys,
                "argv",
                [
                    BOOTSTRAP_PATH.as_posix(), *hashes, frozen_sha,
                    sha256(sources["verdict"]), sha256(sources["report"]),
                ],
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
