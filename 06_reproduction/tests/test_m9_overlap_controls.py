#!/usr/bin/env python3
"""Synthetic rejection matrix for the frozen M9 overlap-only workflow."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import stat
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

FROZEN_SITE_PACKAGES = Path(
    "/home/evan-williams/deeph-m9/env/deeph-v022/lib/python3.9/site-packages"
)
if FROZEN_SITE_PACKAGES.as_posix() not in sys.path:
    sys.path.append(FROZEN_SITE_PACKAGES.as_posix())

import numpy as np


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
CONFIG = Path(__file__).resolve().parents[1] / "configs/m9_overlap_only_contract.json"
sys.path.insert(0, SCRIPTS.as_posix())

import m9_budget
import m9_overlap_source_launcher
from m9_openmx_build import (
    apply_official_patch,
    assert_makefile_contract,
    fixed_build_environment,
    installed_tree_inventory,
    render_makefile,
    safe_extract,
    validated_members,
    verify_packages,
    verify_build_artifact_allowlist,
    verify_mpi_wrapper_compilers,
)
from m9_overlap_common import require_budget_context, write_utf8_lf
from m9_overlap_source_launcher import FrozenSourceLoader, verify_control_directory
from m9_openmx_input import load_structure, render_input, verify_rendered_input
from m9_overlap_contract import (
    expected_command,
    validate_allowlist,
    validate_logs,
    validate_onsite_blocks,
    validate_preparse_outputs,
)
from m9_overlap_executor import compute_projection


def contract() -> dict[str, object]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def tar_bytes(entries: list[tuple[str, bytes, str]]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, payload, kind in entries:
            info = tarfile.TarInfo(name)
            if kind == "file":
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            elif kind == "dir":
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = "target"
                archive.addfile(info)
            else:
                raise AssertionError(kind)
    return buffer.getvalue()


def cleanup_security_gate(parent: Path, migration: Path, gate_path: Path) -> dict[str, object]:
    trust_root = migration.parent
    snapshot = trust_root / "cleanup_gate.verified.json"
    gate = {
        "decision_id": "D-017-source-control-test-cleanup-v1",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
        "authorization_sha256": "a" * 64,
        "frozen_sha256": "f" * 64,
        "audit_report_sha256": "r" * 64,
        "artifact_sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74",
        "runtime_sha256": {"runtime": "x" * 64},
        "cleanup_parent_security": {
            "before": {"path": parent.as_posix(), "uid": 1000, "gid": 1000, "mode": 0o755},
            "hardened": {"path": parent.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770},
            "after": {"path": parent.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770},
        },
        "cleanup_security_migration": {
            "schema_version": "m9-source-control-test-security-migration-v1",
            "path": migration.as_posix(),
        },
        "cleanup_trust_root": {"path": trust_root.as_posix(), "uid": 0, "gid": 0, "mode": 0o700},
        "cleanup_verified_gate_snapshot": {"path": snapshot.as_posix(), "uid": 0, "gid": 0, "mode": 0o600},
    }
    gate_bytes = (json.dumps(gate, sort_keys=True) + "\n").encode("utf-8")
    gate_path.write_bytes(gate_bytes)
    gate_stat = os.lstat(gate_path)
    gate["_verified_gate_bytes"] = gate_bytes
    gate["_verified_gate_sha256"] = hashlib.sha256(gate_bytes).hexdigest()
    gate["_verified_gate_stat"] = {"dev": gate_stat.st_dev, "ino": gate_stat.st_ino, "bytes": gate_stat.st_size, "uid": gate_stat.st_uid, "gid": gate_stat.st_gid, "mode": gate_stat.st_mode & 0o7777, "nlink": gate_stat.st_nlink}
    return gate


class BuildContractTests(unittest.TestCase):
    def test_python39_lf_writer_emits_exact_utf8_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "rendered.txt"
            write_utf8_lf(target, "alpha\nbeta\n")
            self.assertEqual(target.read_bytes(), b"alpha\nbeta\n")
            with self.assertRaises(ValueError):
                write_utf8_lf(target, "alpha\r\nbeta\r\n")
        for script in (
            SCRIPTS / "m9_openmx_build.py",
            SCRIPTS / "m9_openmx_input.py",
        ):
            self.assertNotIn("newline=", script.read_text(encoding="utf-8"))

    def test_makefile_unique_flags_and_negative_matrix(self) -> None:
        make = contract()["software"]["openmx_makefile"]
        base = "CC = old\nFC = old\nLIB = old\n"
        rendered = render_makefile(base, "/frozen/hdf5", make)
        self.assertIn("-fcommon", rendered)
        self.assertIn("-fallow-argument-mismatch", rendered)
        assert_makefile_contract(rendered, "/frozen/hdf5", make)
        with self.assertRaisesRegex(ValueError, "exactly one active CC"):
            render_makefile(base + "CC = duplicate\n", "/frozen/hdf5", make)
        bad_cc = dict(make)
        bad_cc["cc"] = str(bad_cc["cc"]).replace(" -fcommon", "")
        with self.assertRaisesRegex(ValueError, "-fcommon"):
            render_makefile(base, "/frozen/hdf5", bad_cc)
        bad_fc = dict(make)
        bad_fc["fc"] = str(bad_fc["fc"]).replace(" -fallow-argument-mismatch", "")
        with self.assertRaisesRegex(ValueError, "-fallow-argument-mismatch"):
            render_makefile(base, "/frozen/hdf5", bad_fc)

    def test_toolchain_version_drift_is_rejected(self) -> None:
        frozen = contract()
        packages = frozen["software"]["ubuntu_packages"]

        def output(command: list[str], **_: object) -> str:
            if command[0] == "/usr/bin/dpkg-query":
                return str(packages[command[-1]])
            if command[0] == "/usr/bin/gcc":
                return "10.5.0"
            raise AssertionError(command)

        with mock.patch("m9_openmx_build.tool_path", side_effect=lambda c, n: Path("/usr/bin") / n.replace("_query", "-query")), mock.patch(
            "m9_openmx_build.subprocess.check_output", side_effect=output
        ):
            with self.assertRaisesRegex(ValueError, "gcc_dumpversion"):
                verify_packages(frozen)

    def test_build_environment_ignores_caller_path(self) -> None:
        frozen = contract()
        with mock.patch.dict("os.environ", {"PATH": "/tmp/fake-first"}, clear=False):
            environment = fixed_build_environment(frozen)
        self.assertEqual(
            environment["PATH"],
            "/usr/sbin:/usr/bin:/sbin:/bin",
        )
        self.assertNotIn("/tmp/fake-first", environment["PATH"])

    def test_mpi_wrapper_compiler_cannot_resolve_from_usr_local(self) -> None:
        frozen = contract()

        def tool(_: dict[str, object], name: str) -> Path:
            return Path("/usr/bin") / name

        def showme(command: list[str], **_: object) -> str:
            return {"mpicc": "gcc", "mpif90": "gfortran"}[Path(command[0]).name]

        with mock.patch("m9_openmx_build.tool_path", side_effect=tool), mock.patch(
            "m9_openmx_build.subprocess.check_output", side_effect=showme
        ):
            result = verify_mpi_wrapper_compilers(frozen)
        self.assertEqual(result["mpicc"]["resolved"], Path("/usr/bin/gcc").resolve().as_posix())
        self.assertEqual(
            result["mpif90"]["resolved"], Path("/usr/bin/gfortran").resolve().as_posix()
        )

        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / "gcc"
            fake.write_text("fake", encoding="utf-8")
            with mock.patch("m9_openmx_build.tool_path", side_effect=tool), mock.patch(
                "m9_openmx_build.subprocess.check_output", side_effect=showme
            ), mock.patch("m9_openmx_build.shutil.which", return_value=fake.as_posix()):
                with self.assertRaisesRegex(ValueError, "shadowed"):
                    verify_mpi_wrapper_compilers(frozen)

    def test_build_rejects_unregistered_new_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "source").mkdir()
            (root / "source/original.c").write_text("x", encoding="utf-8")
            baseline = {"source/original.c"}
            self.assertEqual(verify_build_artifact_allowlist(root, baseline), [])
            (root / "source/new-provenance.txt").write_text("unexpected", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unregistered file"):
                verify_build_artifact_allowlist(root, baseline)

    def test_hdf5_install_inventory_hashes_every_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "lib").mkdir()
            library = root / "lib/libhdf5.so.200"
            library.write_bytes(b"frozen-hdf5")
            inventory = installed_tree_inventory(root)
            self.assertEqual(inventory["lib/libhdf5.so.200"]["bytes"], 11)
            self.assertEqual(
                inventory["lib/libhdf5.so.200"]["sha256"],
                __import__("hashlib").sha256(b"frozen-hdf5").hexdigest(),
            )

    def test_tar_traversal_link_duplicate_and_patch_placement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, entries in enumerate(
                (
                    [("../escape", b"x", "file")],
                    [("link", b"", "symlink")],
                    [("same", b"1", "file"), ("./same", b"2", "file")],
                )
            ):
                path = root / f"bad-{index}.tar.gz"
                path.write_bytes(tar_bytes(entries))
                with tarfile.open(path, "r:gz") as archive:
                    with self.assertRaises(ValueError):
                        validated_members(archive)
                with self.assertRaises(ValueError):
                    safe_extract(path, root / f"out-{index}")

            patch = root / "patch.tar.gz"
            patch.write_bytes(
                tar_bytes([("openmx.c", b"official", "file"), ("kpoint.in", b"k", "file")])
            )
            openmx = root / "openmx3.9"
            (openmx / "source").mkdir(parents=True)
            (openmx / "work").mkdir()
            written = apply_official_patch(patch, openmx)
            self.assertEqual(written, ["source/openmx.c", "work/kpoint.in"])
            self.assertEqual((openmx / "source/openmx.c").read_bytes(), b"official")
            self.assertEqual((openmx / "work/kpoint.in").read_bytes(), b"k")


class InputContractTests(unittest.TestCase):
    def test_frozen_structure_500_inventory_and_round_trip(self) -> None:
        frozen = contract()
        source = Path(frozen["runtime_paths"]["processed_data"]) / "500"
        loaded = load_structure(source, frozen)
        self.assertEqual(set(loaded["source_sha256"]), {
            "element.dat", "info.json", "lat.dat", "orbital_types.dat",
            "rc.npz", "rh.npz", "rlat.dat", "site_positions.dat",
        })
        data_path = Path(frozen["runtime_paths"]["openmx_data"])
        rendered = render_input(
            "500", data_path, loaded["lattice"], loaded["fractional"], frozen
        )
        result = verify_rendered_input(rendered, "500", data_path, loaded["cartesian"], frozen)
        self.assertLessEqual(result["rendered_round_trip_residual_angstrom"], 1e-12)
        bad = rendered.replace(
            next(line for line in rendered.splitlines() if line.strip().startswith("1 C ")),
            "   1 C 0.0000000000000000 0.0000000000000000 0.0000000000000000 2.0 2.0",
        )
        with self.assertRaisesRegex(ValueError, "rounded rendered input residual"):
            verify_rendered_input(bad, "500", data_path, loaded["cartesian"], frozen)

    def test_input_cli_has_no_root_or_all_escape(self) -> None:
        script = SCRIPTS / "m9_openmx_input.py"
        for arguments in (
            ["--all"],
            ["--structure-id", "500", "--processed-root", "/tmp/alternate"],
            ["--structure-id", "500", "--openmx-data-path", "/tmp/alternate"],
        ):
            result = subprocess.run(
                [sys.executable, "-B", script.as_posix(), *arguments],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stderr.decode())


class ExecutorAndOutputTests(unittest.TestCase):
    def namespace(
        self,
        action: str,
        bucket: str,
        forecast: int,
        structure_id: str | None = None,
        command: list[str] | None = None,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            cpu_bucket=bucket,
            overlap_action=action,
            structure_id=structure_id,
            forecast_bytes=forecast,
            command=[] if command is None else command,
            cwd=None,
            log=None,
        )

    def test_budget_accepts_only_action_api_and_projected_forecast(self) -> None:
        workflow = {
            "stage": "BATCH_RUNNING",
            "hard_stopped": False,
            "next_structure_id": "510",
            "active_structure_id": None,
            "per_structure_forecast_bytes": 12345,
            "apt_install_completed": True,
        }
        result = m9_budget.validate_overlap_request(
            self.namespace("batch_prepare", "overlap_batch", 12345, "510"), workflow
        )
        self.assertEqual(result, ("batch_prepare", "overlap_batch", 12345))
        for args in (
            self.namespace("batch_prepare", "overlap_batch", 0, "510"),
            self.namespace("batch_prepare", "overlap_batch", 12345, "520"),
            self.namespace(
                "batch_prepare",
                "overlap_batch",
                12345,
                "510",
                ["/usr/bin/mpirun", "-forcetest2"],
            ),
        ):
            with self.assertRaises(SystemExit):
                m9_budget.validate_overlap_request(args, workflow)
        audit_workflow = dict(workflow, stage="AUDIT_PASSED", next_structure_id="500", apt_install_completed=False)
        with self.assertRaisesRegex(SystemExit, "below frozen lower bound"):
            m9_budget.validate_overlap_request(
                self.namespace("apt_install", "overlap_build", 0), audit_workflow
            )
        self.assertEqual(
            expected_command(contract()),
            [
                "/usr/bin/mpirun", "--bind-to", "none", "-np", "1",
                "/home/evan-williams/deeph-m9/software/openmx-overlap-build/openmx3.9/source/openmx",
                "openmx.dat",
            ],
        )

    def test_overlap_init_rejects_nonfrozen_python_before_state_write(self) -> None:
        system_python = Path("/usr/bin/python3.10")
        if not system_python.is_file():
            self.skipTest("frozen Ubuntu system Python 3.10 is unavailable")
        script = SCRIPTS / "m9_budget.py"
        workflow = Path("/home/evan-williams/deeph-m9/manifests/overlap_workflow_state.json")
        transaction = Path("/home/evan-williams/deeph-m9/manifests/overlap_transaction.json")
        before = (workflow.exists(), transaction.exists())
        result = subprocess.run(
            [system_python.as_posix(), "-I", "-S", "-B", script.as_posix(), "overlap-init"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        after = (workflow.exists(), transaction.exists())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"requires frozen Python", result.stderr)
        self.assertEqual(after, before)

    def test_environment_spoof_cannot_create_budget_context(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {
                "M9_OVERLAP_BUDGET_WRAPPED": "1",
                "M9_OVERLAP_CPU_BUCKET": "overlap_build",
                "M9_OVERLAP_FORECAST_BYTES": "9999999999",
            },
            clear=False,
        ):
            for bucket, actions in (
                ("overlap_build", ("source_prepare", "source_build")),
                ("overlap_smoke", ("smoke_prepare", "smoke_run", "project")),
                ("overlap_batch", ("batch_prepare", "batch_run")),
            ):
                with self.assertRaisesRegex(RuntimeError, "consumed budget capability"):
                    require_budget_context(bucket, actions)

    def test_source_loader_ignores_valid_malicious_pyc(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "frozen_mod.py"
            source.write_text("VALUE = 'GOOD'\n", encoding="utf-8")
            pycache = root / "__pycache__"
            pycache.mkdir()
            malicious = compile("VALUE = 'MALICIOUS'\n", source.as_posix(), "exec")
            import marshal

            # A syntactically plausible cache is deliberately present; the source-only loader never opens it.
            (pycache / "frozen_mod.cpython-39.pyc").write_bytes(
                importlib.util.MAGIC_NUMBER + b"\0" * 12 + marshal.dumps(malicious)
            )
            expected = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
            loader = FrozenSourceLoader("frozen_mod", source, expected)
            spec = importlib.util.spec_from_loader("frozen_mod", loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
            self.assertEqual(module.VALUE, "GOOD")

    def test_isolated_entry_blocks_adjacent_pyc_and_control_directory_rejects_cache(self) -> None:
        import marshal

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / "launcher.py"
            script.write_text("import argparse\nprint('SAFE')\n", encoding="utf-8")
            malicious = compile("print('MALICIOUS')\nraise SystemExit(0)\n", "argparse.py", "exec")
            (root / "argparse.pyc").write_bytes(
                importlib.util.MAGIC_NUMBER + b"\0" * 12 + marshal.dumps(malicious)
            )
            unsafe = subprocess.run(
                [sys.executable, "-B", script.as_posix()],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            isolated = subprocess.run(
                [sys.executable, "-I", "-S", "-B", script.as_posix()],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertIn(b"MALICIOUS", unsafe.stdout)
            self.assertNotIn(b"MALICIOUS", isolated.stdout)
            self.assertIn(b"SAFE", isolated.stdout)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment = root / "venv"
            subprocess.run(
                [sys.executable, "-m", "venv", environment.as_posix()],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            site_packages = environment / "lib" / version / "site-packages"
            (site_packages / "malicious.pth").write_text(
                "import sys; print('MALICIOUS_PTH')\n", encoding="utf-8"
            )
            body = root / "body.py"
            body.write_text("print('SAFE_BODY')\n", encoding="utf-8")
            python = environment / "bin/python"
            unsafe_site = subprocess.run(
                [python.as_posix(), "-I", "-B", body.as_posix()],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            no_site = subprocess.run(
                [python.as_posix(), "-I", "-S", "-B", body.as_posix()],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertIn(b"MALICIOUS_PTH", unsafe_site.stdout)
            self.assertNotIn(b"MALICIOUS_PTH", no_site.stdout)
            self.assertEqual(no_site.stdout.strip(), b"SAFE_BODY")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "allowed.py").write_text("VALUE = 1\n", encoding="utf-8")
            verify_control_directory(root, {"allowed.py"})
            (root / "argparse.py").write_text("raise SystemExit\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "unfrozen"):
                verify_control_directory(root, {"allowed.py"})
            (root / "argparse.py").unlink()
            (root / "__pycache__").mkdir()
            with self.assertRaisesRegex(RuntimeError, "subdirectory"):
                verify_control_directory(root, {"allowed.py"})

    def populate_allowlist(self, root: Path, frozen: dict[str, object]) -> None:
        allowed = frozen["output_contract"]["run_file_allowlist_before_report"]
        for relative in allowed:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"")

    def test_strict_output_allowlist_and_log_markers(self) -> None:
        frozen = contract()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.populate_allowlist(root, frozen)
            markers = frozen["output_contract"]["required_stdout_markers"]
            (root / "openmx.std").write_text("\n".join(markers), encoding="utf-8")
            (root / "openmx.err").write_text("", encoding="utf-8")
            (root / "openmx.out").write_text("overlap-only", encoding="utf-8")
            validate_allowlist(root, frozen)
            validate_logs(root, frozen)
            extra = root / "parsed/HAMILTONIANS.H5"
            extra.write_bytes(b"forbidden")
            with self.assertRaisesRegex(ValueError, "allowlist mismatch"):
                validate_allowlist(root, frozen)
            extra.unlink()
            (root / "openmx.out").write_text("SCF ITERATION", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SCF log marker"):
                validate_logs(root, frozen)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in frozen["output_contract"]["run_file_allowlist_before_parser"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"")
            (root / "openmx.std").write_text("\n".join(markers), encoding="utf-8")
            (root / "openmx.out").write_text("overlap-only", encoding="utf-8")
            validate_preparse_outputs(root, frozen)
            (root / "output/energy.HDF5").write_bytes(b"forbidden")
            with self.assertRaisesRegex(ValueError, "pre-parser output allowlist"):
                validate_preparse_outputs(root, frozen)

    def test_all_onsite_blocks_must_be_symmetric_positive_definite(self) -> None:
        matrices = {
            (0, 0, 0, atom, atom): np.eye(13, dtype=np.float64)
            for atom in range(1, 73)
        }
        residual, minimum = validate_onsite_blocks(matrices, 1e-10)
        self.assertEqual(residual, 0.0)
        self.assertEqual(minimum, 1.0)
        matrices[(0, 0, 0, 17, 17)] = np.eye(13, dtype=np.float64)
        matrices[(0, 0, 0, 17, 17)][0, 1] = 1e-5
        with self.assertRaisesRegex(ValueError, "atom-17 onsite symmetry"):
            validate_onsite_blocks(matrices, 1e-10)


class BudgetProjectionTests(unittest.TestCase):
    @contextlib.contextmanager
    def source_recovery_tree(self, root: Path):
        manifests = root / "manifests"
        capabilities = manifests / "overlap_capabilities"
        manifests.mkdir()
        capabilities.mkdir()
        paths = {
            "state": manifests / "budget_state.json",
            "workflow": manifests / "overlap_workflow_state.json",
            "transaction": manifests / "overlap_transaction.json",
            "ledger": manifests / "budget_ledger.jsonl",
            "lock": manifests / "budget.lock",
            "recovery": manifests / "overlap_source_control_recovery.json",
            "parent": manifests / "overlap_source_control_recovery_parent.json",
            "gate": manifests / "overlap_source_control_recovery_gate.json",
        }
        paths["lock"].touch()
        state = {
            "schema_version": "m9-budget-state-v1",
            "hard_stopped": True,
            "active_overlap_transaction": None,
        }
        workflow = {
            "schema_version": "m9-overlap-workflow-state-v1",
            "stage": "HARD_STOP",
            "hard_stopped": True,
            "active_transaction": None,
            "apt_install_completed": True,
        }
        tx = {
            "schema_version": "m9-overlap-transaction-v1",
            "transaction_id": "parent-source-prepare",
            "state": "FAILED_COMMITTED",
            "action": "source_prepare",
            "bucket": "overlap_build",
        }
        parent_events = [
            {"event_id": "parent:one", "event": "PARENT", "value": 1},
            {"event_id": "parent:two", "event": "PARENT", "value": 2},
        ]
        paths["state"].write_text(json.dumps(state), encoding="utf-8")
        paths["workflow"].write_text(json.dumps(workflow), encoding="utf-8")
        paths["transaction"].write_text(json.dumps(tx), encoding="utf-8")
        paths["ledger"].write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in parent_events),
            encoding="utf-8",
        )
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            os.chown(paths["ledger"], 1000, 1000)
        paths["gate"].write_bytes(b"source-control-gate")
        capability_id = "1" * 32
        capability = capabilities / f"{capability_id}.json"
        capability.write_text(
            json.dumps(
                {
                    "schema_version": "m9-overlap-capability-v1",
                    "state": "BOUND",
                    "capability_id": capability_id,
                    "transaction_id": tx["transaction_id"],
                    "action": "source_prepare",
                }
            ),
            encoding="utf-8",
        )
        capability.chmod(0o600)
        bootstrap = {
            "isolated": True,
            "no_site": True,
            "dont_write_bytecode": True,
            "python_executable": "/frozen/python3.9",
            "sys_path": ["/frozen/lib/python3.9"],
            "modules": {"json": {"sha256": "b" * 64}},
        }
        gate = {
            "decision_id": "D-017-source-control-recovery-v1",
            "audit_report_path": "/audit/verdict.json",
            "audit_report_sha256": "a" * 64,
            "authorization_record_sha256": "c" * 64,
            "frozen_hashes_sha256": "d" * 64,
        }
        products = tuple(root / f"missing-product-{index}" for index in range(6))
        with contextlib.ExitStack() as stack:
            stack.enter_context(
                mock.patch.multiple(
                    m9_budget,
                    STATE_PATH=paths["state"],
                    OVERLAP_WORKFLOW_STATE=paths["workflow"],
                    OVERLAP_TRANSACTION=paths["transaction"],
                    LEDGER_PATH=paths["ledger"],
                    LOCK_PATH=paths["lock"],
                    SOURCE_CONTROL_RECOVERY_TRANSACTION=paths["recovery"],
                    SOURCE_CONTROL_RECOVERY_PARENT=paths["parent"],
                    SOURCE_CONTROL_RECOVERY_GATE=paths["gate"],
                    OVERLAP_CAPABILITY_ROOT=capabilities,
                    SOURCE_RECOVERY_PRODUCTS=products,
                )
            )
            stack.enter_context(mock.patch.object(m9_budget.os, "geteuid", return_value=0))
            stack.enter_context(mock.patch.object(m9_budget, "preserve_owner", return_value=None))
            stack.enter_context(
                mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value=bootstrap)
            )
            stack.enter_context(
                mock.patch.object(
                    m9_budget,
                    "verify_source_control_recovery_gate_and_hashes",
                    return_value=gate,
                )
            )
            stack.enter_context(
                mock.patch.object(
                    m9_budget,
                    "source_control_preflight",
                    return_value=(tx, capability, m9_budget.file_stat_receipt(capability)),
                )
            )
            stack.enter_context(mock.patch.object(m9_budget.secrets, "token_hex", return_value="a" * 32))
            stack.enter_context(mock.patch.object(m9_budget, "utc_now", return_value="2026-08-19T00:00:00Z"))
            yield {
                "paths": paths,
                "capabilities": capabilities,
                "capability": capability,
                "bootstrap": bootstrap,
                "gate": gate,
                "tx": tx,
                "parent_events": parent_events,
            }

    @contextlib.contextmanager
    def source_gate_disposition_tree(self, root: Path):
        manifests = root / "manifests"
        controls = root / "root-control"
        manifests.mkdir()
        controls.mkdir()
        active = manifests / "overlap_source_control_recovery_gate.json"
        retired = manifests / "overlap_source_control_recovery_gate.closed-set-invalid.retired.json"
        journal = controls / "source-control-gate-disposition.json"
        lock = manifests / "budget.lock"
        lock.touch()
        replacement_verdict_path = root / "replacement.json"
        disposition_verdict_path = root / "disposition.json"
        frozen = root / "frozen.json"
        auth = root / "authorization.md"
        old_gate = {
            "schema_version": "m9-source-control-recovery-gate-v1",
            "status": "PASS", "blocking": 0, "non_blocking": 0,
            "decision_id": "D-017-source-control-recovery-v1",
            "audit_report_path": "/old/verdict.json",
            "audit_report_sha256": "1" * 64,
            "authorization_record_path": auth.as_posix(),
            "authorization_record_sha256": "2" * 64,
            "frozen_hashes_path": frozen.as_posix(),
            "frozen_hashes_sha256": "3" * 64,
            "expected_failed_transaction": {"transaction_id": "parent", "sha256": "4" * 64},
            "expected_state_sha256": "5" * 64,
            "expected_workflow_sha256": "6" * 64,
            "expected_ledger_sha256": "7" * 64,
            "expected_stale_capability": {"capability_id": "cap"},
        }
        active.write_text(json.dumps(old_gate), encoding="utf-8"); active.chmod(0o600)
        replacement_verdict = {
            "schema_version": "m9-source-control-recovery-audit-verdict-v1",
            "decision_id": "D-017-source-control-recovery-v1",
            "verdict": "PASS", "blocking": 0, "non_blocking": 0,
        }
        replacement_verdict_path.write_text(json.dumps(replacement_verdict), encoding="utf-8")
        disposition_verdict_path.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
        frozen.write_text("{}", encoding="utf-8"); auth.write_text("authorized", encoding="utf-8")
        runtime = {"state_sha256": "a" * 64, "workflow_sha256": "b" * 64}
        disposition = {
            "runtime_sha256": runtime,
            "old_gate_sha256": hashlib.sha256(active.read_bytes()).hexdigest(),
            "old_gate_bytes": active.stat().st_size,
        }
        bootstrap = {"python_executable": "/frozen/python3.9", "isolated": True, "no_site": True, "dont_write_bytecode": True}

        def private_read(path: Path) -> tuple[dict[str, object], bytes]:
            flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
            try:
                descriptor = os.open(path, flags)
            except OSError as exc:
                raise SystemExit("root-private control object is missing or not regular") from exc
            try:
                before = os.fstat(descriptor)
                if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                    raise SystemExit("root-private control object metadata mismatch")
                chunks = []
                while True:
                    chunk = os.read(descriptor, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                payload = b"".join(chunks)
                after = os.fstat(descriptor)
                linked = os.lstat(path)
                stable = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
                if (
                    any(getattr(before, field) != getattr(after, field) for field in stable)
                    or any(getattr(after, field) != getattr(linked, field) for field in stable)
                    or stat.S_ISLNK(linked.st_mode)
                    or len(payload) != after.st_size
                ):
                    raise SystemExit("root-private control object path changed while reading")
            finally:
                os.close(descriptor)
            return ({
                "path": Path(path).as_posix(), "bytes": after.st_size,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1,
            }, payload)

        def private_bytes(path: Path, payload: bytes) -> None:
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_bytes(payload); temporary.chmod(0o600); os.replace(temporary, path); path.chmod(0o600)

        def private_json(path: Path, value: dict) -> None:
            private_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.multiple(
                m9_budget,
                SOURCE_CONTROL_RECOVERY_GATE=active,
                SOURCE_CONTROL_GATE_INVALID_RETIRED=retired,
                SOURCE_CONTROL_GATE_DISPOSITION_JOURNAL=journal,
                SOURCE_CONTROL_RECOVERY_REPLACEMENT_VERDICT=replacement_verdict_path,
                SOURCE_CONTROL_GATE_DISPOSITION_VERDICT=disposition_verdict_path,
                SOURCE_CONTROL_RECOVERY_FROZEN_HASHES=frozen,
                SOURCE_CONTROL_RECOVERY_AUTHORIZATION=auth,
                SOURCE_CONTROL_RECOVERY_TRANSACTION=manifests / "missing-recovery.json",
                SOURCE_CONTROL_RECOVERY_PARENT=manifests / "missing-parent.json",
                LOCK_PATH=lock,
                INVALID_SOURCE_CONTROL_GATE_SHA256=disposition["old_gate_sha256"],
                INVALID_SOURCE_CONTROL_GATE_BYTES=disposition["old_gate_bytes"],
            ))
            stack.enter_context(mock.patch.object(m9_budget.os, "geteuid", return_value=0))
            stack.enter_context(mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value=bootstrap))
            stack.enter_context(mock.patch.object(m9_budget, "verify_source_control_gate_disposition", return_value=(disposition, replacement_verdict)))
            stack.enter_context(mock.patch.object(
                m9_budget,
                "verify_source_control_recovery_gate_and_hashes",
                side_effect=lambda: json.loads(active.read_text(encoding="utf-8")),
            ))
            stack.enter_context(mock.patch.object(m9_budget, "source_control_disposition_runtime_receipt", return_value=runtime))
            stack.enter_context(mock.patch.object(m9_budget, "read_strict_root_private_bytes", side_effect=private_read))
            stack.enter_context(mock.patch.object(m9_budget, "atomic_root_private_bytes", side_effect=private_bytes))
            stack.enter_context(mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=private_json))
            stack.enter_context(mock.patch.object(m9_budget, "utc_now", return_value="2026-08-19T00:00:00Z"))
            yield {
                "active": active, "retired": retired, "journal": journal,
                "lock": lock, "runtime": runtime, "bootstrap": bootstrap,
            }

    @contextlib.contextmanager
    def source_gate_lock_refresh_tree(self, root: Path):
        with self.source_gate_disposition_tree(root) as base:
            active = base["active"]
            pre_retired = active.with_name("overlap_source_control_recovery_gate.pre-lock-mode-refresh.retired.json")
            refresh_journal = root / "root-control/source-control-gate-lock-refresh.json"
            refresh_verdict_path = root / "lock-refresh-verdict.json"
            replacement_verdict_path = root / "lock-refresh-replacement.json"
            refresh_verdict_path.write_text('{"verdict":"PASS"}', encoding="utf-8")
            replacement_verdict = {
                "schema_version": "m9-source-control-recovery-audit-verdict-v1",
                "decision_id": "D-017-source-control-recovery-v1",
                "verdict": "PASS", "blocking": 0, "non_blocking": 0,
            }
            replacement_verdict_path.write_text(json.dumps(replacement_verdict), encoding="utf-8")
            runtime = {"state_sha256": "c" * 64, "disposition_journal_sha256": "d" * 64}
            refresh_verdict = {
                "runtime_sha256": runtime,
                "old_gate_sha256": hashlib.sha256(active.read_bytes()).hexdigest(),
                "old_gate_bytes": active.stat().st_size,
            }
            bindings = {
                "refresh_verdict_sha256": hashlib.sha256(refresh_verdict_path.read_bytes()).hexdigest(),
                "replacement_verdict_sha256": hashlib.sha256(replacement_verdict_path.read_bytes()).hexdigest(),
                "frozen_hashes_sha256": hashlib.sha256(
                    m9_budget.SOURCE_CONTROL_RECOVERY_FROZEN_HASHES.read_bytes()
                ).hexdigest(),
                "authorization_record_sha256": hashlib.sha256(
                    m9_budget.SOURCE_CONTROL_RECOVERY_AUTHORIZATION.read_bytes()
                ).hexdigest(),
            }
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.multiple(
                    m9_budget,
                    SOURCE_CONTROL_GATE_LOCK_REFRESH_VERDICT=refresh_verdict_path,
                    SOURCE_CONTROL_RECOVERY_LOCK_REPLACEMENT_VERDICT=replacement_verdict_path,
                    SOURCE_CONTROL_GATE_PRE_LOCK_RETIRED=pre_retired,
                    SOURCE_CONTROL_GATE_LOCK_REFRESH_JOURNAL=refresh_journal,
                    PRE_LOCK_REFRESH_GATE_SHA256=refresh_verdict["old_gate_sha256"],
                    PRE_LOCK_REFRESH_GATE_BYTES=refresh_verdict["old_gate_bytes"],
                ))
                stack.enter_context(mock.patch.object(
                    m9_budget, "verify_source_control_gate_lock_refresh",
                    return_value=(refresh_verdict, replacement_verdict, bindings),
                ))
                stack.enter_context(mock.patch.object(
                    m9_budget, "source_control_lock_refresh_runtime_receipt", return_value=runtime,
                ))
                yield {
                    **base,
                    "pre_retired": pre_retired,
                    "refresh_journal": refresh_journal,
                    "refresh_runtime": runtime,
                    "refresh_verdict": refresh_verdict,
                    "replacement_verdict": replacement_verdict,
                    "replacement_verdict_path": replacement_verdict_path,
                    "bindings": bindings,
                }

    @staticmethod
    def file_bytes(paths: list[Path]) -> dict[str, bytes | None]:
        return {path.as_posix(): path.read_bytes() if path.exists() else None for path in paths}

    def status(self) -> dict[str, object]:
        return {
            "deadline_remaining_seconds": 100000.0,
            "cpu_seconds": {"overlap_build": 0.0, "overlap_smoke": 0.0, "overlap_batch": 0.0},
            "storage": {
                "combined_apparent_bytes_since_overlap_baseline": 0,
                "combined_allocated_bytes_since_overlap_baseline": 0,
                "host_vhdx_growth_since_overlap_baseline_bytes": 0,
                "combined_apparent_bytes": 0,
                "combined_allocated_bytes": 0,
                "host_vhdx_growth_from_start_bytes": 0,
            },
            "violations": [],
        }

    def test_projection_pass_and_each_resource_failure(self) -> None:
        frozen = contract()
        state = {
            "completed_structure_ids": ["500"],
            "smoke_elapsed_seconds": 1.0,
            "smoke_payload_increment_bytes": 1,
        }
        self.assertEqual(compute_projection(frozen, state, self.status())["status"], "PASS")
        cpu_state = dict(state, smoke_elapsed_seconds=100.0)
        self.assertIn(
            "projected_overlap_batch_cpu",
            compute_projection(frozen, cpu_state, self.status())["reasons"],
        )
        storage_state = dict(state, smoke_payload_increment_bytes=30_000_000)
        self.assertTrue(
            any(
                "overlap_baseline" in reason
                for reason in compute_projection(frozen, storage_state, self.status())["reasons"]
            )
        )
        with self.assertRaisesRegex(ValueError, "exactly the validated smoke"):
            compute_projection(frozen, dict(state, completed_structure_ids=[]), self.status())

    def test_budget_negative_forecast_and_overlap_sublimit(self) -> None:
        state = {
            "hard_stopped": False,
            "gpu_seconds": {name: 0.0 for name in m9_budget.GPU_LIMITS},
            "cpu_seconds": {name: 0.0 for name in m9_budget.CPU_LIMITS},
            "overlap_storage_baseline": {},
        }
        snapshot = {
            "project_audit_apparent_bytes": 0,
            "combined_apparent_bytes": 0,
            "combined_allocated_bytes": 0,
            "host_vhdx_growth_from_start_bytes": 0,
            "combined_apparent_bytes_since_overlap_baseline": 0,
            "combined_allocated_bytes_since_overlap_baseline": 0,
            "host_vhdx_growth_since_overlap_baseline_bytes": 0,
        }
        with mock.patch.object(m9_budget, "deadline_remaining", return_value=1000.0), mock.patch.object(
            m9_budget, "storage_snapshot", return_value=snapshot
        ):
            self.assertIn("negative_forecast_bytes", m9_budget.violations(state, -1))
            reasons = m9_budget.violations(state, m9_budget.OVERLAP_STORAGE_LIMIT + 1)
            self.assertIn("combined_apparent_bytes_since_overlap_baseline", reasons)

    def test_failure_commits_budget_and_workflow_hard_stop(self) -> None:
        for reason in ("apt_failed", "controller_sigkill", "command_timeout"):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                state_path = root / "budget.json"
                workflow_path = root / "workflow.json"
                transaction_path = root / "transaction.json"
                ledger_path = root / "ledger.jsonl"
                budget_state = {
                    "hard_stopped": False,
                    "gpu_seconds": {name: 0.0 for name in m9_budget.GPU_LIMITS},
                    "cpu_seconds": {name: 0.0 for name in m9_budget.CPU_LIMITS},
                    "vhdx_baseline_bytes": 0,
                }
                workflow = {"hard_stopped": False, "stage": "AUDIT_PASSED"}
                transaction = {
                    "schema_version": "m9-overlap-transaction-v1",
                    "transaction_id": "a" * 32,
                    "state": "RUNNING",
                }
                snapshot = {
                    "linux_apparent_bytes": 0,
                    "linux_allocated_bytes": 0,
                    "project_audit_apparent_bytes": 0,
                    "project_audit_allocated_bytes": 0,
                    "combined_apparent_bytes": 0,
                    "combined_allocated_bytes": 0,
                    "host_vhdx_bytes": 0,
                    "host_vhdx_growth_from_start_bytes": 0,
                }
                ledger_path.write_text(
                    json.dumps({"event_id": "baseline", "event": "BASELINE"}, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                if hasattr(os, "geteuid") and os.geteuid() == 0:
                    os.chown(ledger_path, 1000, 1000)
                with mock.patch.multiple(
                    m9_budget,
                    STATE_PATH=state_path,
                    OVERLAP_WORKFLOW_STATE=workflow_path,
                    OVERLAP_TRANSACTION=transaction_path,
                    LEDGER_PATH=ledger_path,
                ), mock.patch.object(m9_budget, "storage_snapshot", return_value=snapshot):
                    m9_budget.hard_stop_both(
                        budget_state, workflow, [reason], transaction, "b" * 64
                    )
                saved_budget = json.loads(state_path.read_text(encoding="utf-8"))
                saved_workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
                saved_transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
                self.assertTrue(saved_budget["hard_stopped"])
                self.assertTrue(saved_workflow["hard_stopped"])
                self.assertEqual(saved_workflow["stage"], "HARD_STOP")
                self.assertEqual(saved_transaction["state"], "FAILED_COMMITTED")

    def test_offline_recovery_manifest_and_source_chain(self) -> None:
        manifest, paths = m9_budget.recovery_manifest()
        self.assertEqual(len(paths), 45)
        self.assertEqual(len({item["package"] for item in manifest["packages"]}), 45)
        self.assertTrue(all("depends" in item and "pre_depends" in item for item in manifest["packages"]))
        recovery = json.loads(
            m9_budget.OVERLAP_RECOVERY_TRANSACTION.read_text(encoding="utf-8")
        )
        expected_receipts = {
            "keyring": manifest["repository"]["keyring_sha256"],
            "jammy_inrelease": manifest["repository"]["inrelease"]["jammy"],
            "jammy_updates_inrelease": manifest["repository"]["inrelease"]["jammy-updates"],
            "jammy_main_amd64": manifest["repository"]["packages_index_sha256"]["jammy-main-amd64"],
            "jammy_universe_amd64": manifest["repository"]["packages_index_sha256"]["jammy-universe-amd64"],
            "jammy_updates_main_amd64": manifest["repository"]["packages_index_sha256"]["jammy-updates-main-amd64"],
            "jammy_updates_universe_amd64": manifest["repository"]["packages_index_sha256"]["jammy-updates-universe-amd64"],
        }
        self.assertEqual(recovery["state"], "SUCCESS_COMMITTED")
        self.assertEqual(recovery["source_index_receipts"], expected_receipts)

    def test_offline_recovery_uses_network_namespace_and_credit_formula(self) -> None:
        command = m9_budget.recovery_isolated_command(["/usr/bin/dpkg", "--audit"])
        self.assertEqual(command[:3], ["/usr/bin/unshare", "--net", "--"])
        state = {
            "cpu_seconds": {"overlap_build": 7200.075310528, "overlap_smoke": 0.0, "overlap_batch": 0.0},
            "cpu_adjustments": [{"bucket": "overlap_build", "credited_seconds": 7200.075310528}],
        }
        self.assertEqual(m9_budget.effective_cpu_seconds(state, "overlap_build"), 0.0)

    def test_recovery_manifest_refuses_archive_mutation(self) -> None:
        manifest = json.loads(
            Path(m9_budget.OFFLINE_APT_MANIFEST).read_text(encoding="utf-8")
        )
        original = manifest["packages"][0]["sha256"]
        manifest["packages"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / "manifest.json"
            fake.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(m9_budget, "OFFLINE_APT_MANIFEST", fake):
                with self.assertRaisesRegex(SystemExit, "SHA-256 mismatch"):
                    m9_budget.recovery_manifest()
        self.assertNotEqual(manifest["packages"][0]["sha256"], original)

    def test_recovery_preflight_classifies_complete_partition(self) -> None:
        statuses = {"autoconf": "\tunknown ok not-installed"}
        result = m9_budget.classify_recovery_preflight(statuses, ["autoconf", "m4"])
        self.assertEqual(result["placeholder_count"], 1)
        self.assertEqual(result["absent_count"], 1)
        self.assertEqual(result["installed_count"], 0)
        self.assertEqual(result["unsafe_count"], 0)

    def test_recovery_dpkg_query_rejects_unexpected_diagnostic(self) -> None:
        completed = mock.Mock(returncode=1, stdout="", stderr="dpkg database unavailable\n")
        with mock.patch.object(m9_budget.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(SystemExit, "unexpected diagnostic"):
                m9_budget.recovery_dpkg_query(["m4"])

    def test_recovery_dpkg_query_requires_complete_missing_partition(self) -> None:
        for completed in (
            mock.Mock(returncode=1, stdout="", stderr=""),
            mock.Mock(returncode=1, stdout="", stderr="dpkg-query: no packages found matching a\n"),
            mock.Mock(returncode=0, stdout="", stderr=""),
        ):
            with mock.patch.object(m9_budget.subprocess, "run", return_value=completed):
                with self.assertRaises(SystemExit):
                    m9_budget.recovery_dpkg_query(["a", "b"])

    def test_source_control_recovery_requires_root_gate(self) -> None:
        with mock.patch.object(m9_budget.os, "geteuid", return_value=1000):
            with self.assertRaisesRegex(SystemExit, "requires root"):
                m9_budget.command_overlap_recover_source_control_failure(mock.Mock())

    def test_source_control_recovery_gate_is_separate_from_offline_gate(self) -> None:
        self.assertNotEqual(m9_budget.SOURCE_CONTROL_RECOVERY_GATE, m9_budget.OVERLAP_RECOVERY_GATE)
        self.assertIn("source_control", m9_budget.SOURCE_CONTROL_RECOVERY_TRANSACTION.name)

    def test_source_control_frozen_set_covers_entire_control_directory(self) -> None:
        expected = {
            path.resolve(strict=False)
            for path in m9_budget.OVERLAP_CONTROL_DIRECTORY.glob("*.py")
        }
        frozen_python = {
            path.resolve(strict=False)
            for path in m9_budget.SOURCE_RECOVERY_CONTROL_FILES
            if path.parent.resolve(strict=False)
            == m9_budget.OVERLAP_CONTROL_DIRECTORY.resolve(strict=False)
            and path.suffix == ".py"
        }
        self.assertEqual(frozen_python, expected)

    def test_source_control_event_payload_is_idempotent(self) -> None:
        event = {"event_id": "test-source-recovery", "event": "X", "value": 1}
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Path(temporary) / "ledger.jsonl"
            ledger.write_text(
                json.dumps({"event_id": "baseline", "event": "BASELINE"}, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                os.chown(ledger, 1000, 1000)
            with mock.patch.object(m9_budget, "LEDGER_PATH", ledger):
                m9_budget.append_event_once(event)
                m9_budget.append_event_once(event)
                with self.assertRaises(ValueError):
                    m9_budget.append_event_once({"event_id": "test-source-recovery", "event": "X", "value": 2})

    def test_existing_ledger_append_never_requests_create_and_preserves_inode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Path(temporary) / "ledger.jsonl"
            ledger.write_bytes(b'{"event":"BASELINE"}\n')
            before = os.lstat(ledger)
            original_open = os.open
            observed_flags = []

            def guarded_open(path, flags, *args, **kwargs):
                if Path(path) == ledger:
                    observed_flags.append(flags)
                    self.assertFalse(flags & os.O_CREAT)
                    self.assertTrue(flags & os.O_APPEND)
                return original_open(path, flags, *args, **kwargs)

            with mock.patch.object(m9_budget.os, "open", side_effect=guarded_open):
                m9_budget.append_existing_regular_bytes(
                    ledger,
                    b'{"event":"RECOVERY"}\n',
                    expected_uid=before.st_uid,
                    expected_gid=before.st_gid,
                    expected_mode=stat.S_IMODE(before.st_mode),
                )
            after = os.lstat(ledger)
            self.assertEqual(len(observed_flags), 1)
            self.assertEqual((after.st_dev, after.st_ino, after.st_uid, after.st_gid, after.st_nlink), (before.st_dev, before.st_ino, before.st_uid, before.st_gid, 1))
            self.assertEqual(ledger.read_bytes(), b'{"event":"BASELINE"}\n{"event":"RECOVERY"}\n')

    def test_existing_ledger_append_rejects_symlink_and_hardlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = root / "ledger.jsonl"
            ledger.write_bytes(b"baseline\n")
            current = os.lstat(ledger)
            hardlink = root / "other.jsonl"
            os.link(ledger, hardlink)
            with self.assertRaisesRegex(ValueError, "metadata mismatch"):
                m9_budget.append_existing_regular_bytes(
                    ledger, b"event\n", expected_uid=current.st_uid,
                    expected_gid=current.st_gid, expected_mode=stat.S_IMODE(current.st_mode),
                )
            hardlink.unlink()
            symlink = root / "link.jsonl"
            symlink.symlink_to(ledger)
            with self.assertRaisesRegex(ValueError, "metadata mismatch"):
                m9_budget.append_existing_regular_bytes(
                    symlink, b"event\n", expected_uid=current.st_uid,
                    expected_gid=current.st_gid, expected_mode=stat.S_IMODE(current.st_mode),
                )

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_existing_uid1000_ledger_append_under_sticky_protected_regular(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m9-ledger-protected-") as temporary:
            root = Path(temporary)
            os.chown(root, 0, 1000)
            root.chmod(0o1770)
            ledger = root / "budget_ledger.jsonl"
            ledger.write_bytes(b'{"event":"BASELINE"}\n')
            os.chown(ledger, 1000, 1000)
            ledger.chmod(0o644)
            m9_budget.append_existing_regular_bytes(
                ledger, b'{"event":"RECOVERY"}\n'
            )
            current = os.lstat(ledger)
            self.assertEqual((current.st_uid, current.st_gid, stat.S_IMODE(current.st_mode), current.st_nlink), (1000, 1000, 0o644, 1))
            self.assertEqual(ledger.read_bytes(), b'{"event":"BASELINE"}\n{"event":"RECOVERY"}\n')

    def test_ledger_prefix_binding_and_partial_append_resume(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Path(temporary) / "ledger.jsonl"
            prefix = b'{"event":"BASELINE"}\n'
            event = b'{"event":"RECOVERY"}\n'
            ledger.write_bytes(prefix)
            current = os.lstat(ledger)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                m9_budget.append_existing_regular_bytes(
                    ledger, event, expected_uid=current.st_uid, expected_gid=current.st_gid,
                    expected_mode=stat.S_IMODE(current.st_mode), expected_prefix_bytes=len(prefix),
                    expected_prefix_sha256="0" * 64,
                )
            real_write = os.write

            def short_write(descriptor, payload):
                return real_write(descriptor, payload[:5])

            with mock.patch.object(m9_budget.os, "write", side_effect=short_write):
                with self.assertRaisesRegex(OSError, "short"):
                    m9_budget.append_existing_regular_bytes(
                        ledger, event, expected_uid=current.st_uid, expected_gid=current.st_gid,
                        expected_mode=stat.S_IMODE(current.st_mode), expected_prefix_bytes=len(prefix),
                        expected_prefix_sha256=hashlib.sha256(prefix).hexdigest(),
                    )
            self.assertEqual(ledger.read_bytes(), prefix)
            ledger.write_bytes(prefix)

            def mutate_prefix_then_append(descriptor, payload):
                with ledger.open("r+b") as handle:
                    handle.write(b'X' * len(prefix))
                    handle.flush()
                return real_write(descriptor, payload)

            with mock.patch.object(m9_budget.os, "write", side_effect=mutate_prefix_then_append):
                with self.assertRaisesRegex(ValueError, "changed during write"):
                    m9_budget.append_existing_regular_bytes(
                        ledger, event, expected_uid=current.st_uid, expected_gid=current.st_gid,
                        expected_mode=stat.S_IMODE(current.st_mode), expected_prefix_bytes=len(prefix),
                        expected_prefix_sha256=hashlib.sha256(prefix).hexdigest(),
                    )
            ledger.write_bytes(prefix + event[:7])
            self.assertTrue(
                m9_budget.resume_partial_existing_append(
                    ledger, prefix_bytes=len(prefix), prefix_sha256=hashlib.sha256(prefix).hexdigest(),
                    expected_suffix=event, expected_uid=current.st_uid, expected_gid=current.st_gid,
                    expected_mode=stat.S_IMODE(current.st_mode),
                )
            )
            self.assertEqual(ledger.read_bytes(), prefix)

    @unittest.skipUnless(hasattr(os, "geteuid") and os.geteuid() == 0, "requires root")
    def test_owned_atomic_json_resumes_uid1000_temp_under_sticky_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m9-owned-atomic-") as temporary:
            root = Path(temporary)
            os.chown(root, 0, 1000); root.chmod(0o1770)
            target = root / "runtime.json"
            target.write_text("{}\n", encoding="utf-8"); os.chown(target, 1000, 1000); target.chmod(0o644)
            stale = target.with_suffix(".json.tmp")
            stale.write_text("partial", encoding="utf-8"); os.chown(stale, 1000, 1000); stale.chmod(0o644)
            m9_budget.atomic_owned_json(target, {"state": "COMMITTED"})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"state": "COMMITTED"})
            current = os.lstat(target)
            self.assertEqual((current.st_uid, current.st_gid, stat.S_IMODE(current.st_mode), current.st_nlink), (1000, 1000, 0o644, 1))
            self.assertFalse(stale.exists())
            stale.touch(); stale.chmod(0o600)
            self.assertEqual((os.lstat(stale).st_uid, os.lstat(stale).st_size), (0, 0))
            m9_budget.atomic_owned_json(target, {"state": "RESUMED_FROM_ROOT_EMPTY_TMP"})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["state"], "RESUMED_FROM_ROOT_EMPTY_TMP")

    def test_post_failure_immutable_runtime_rechecks_workflow_and_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = {name: root / f"{name}.json" for name in ("parent", "transaction", "state", "workflow", "retired", "recovery")}
            ledger = root / "ledger.jsonl"
            for name, path in paths.items():
                path.write_text(json.dumps({"name": name}), encoding="utf-8")
            ledger.write_text(json.dumps({"event_id": "parent", "event": "PARENT"}) + "\n", encoding="utf-8")
            runtime = {
                "parent_snapshot_sha256": hashlib.sha256(paths["parent"].read_bytes()).hexdigest(),
                "parent_transaction_sha256": hashlib.sha256(paths["transaction"].read_bytes()).hexdigest(),
                "state_sha256": hashlib.sha256(paths["state"].read_bytes()).hexdigest(),
                "workflow_sha256": hashlib.sha256(paths["workflow"].read_bytes()).hexdigest(),
                "ledger_sha256": hashlib.sha256(ledger.read_bytes()).hexdigest(),
                "retired_capability_path": paths["retired"].as_posix(),
                "retired_capability_sha256": hashlib.sha256(paths["retired"].read_bytes()).hexdigest(),
                "recovery_event_id": "recovery:event", "recovery_event_count": 0,
                "recovery_transaction_sha256": hashlib.sha256(paths["recovery"].read_bytes()).hexdigest(),
            }
            with mock.patch.multiple(
                m9_budget, SOURCE_CONTROL_RECOVERY_PARENT=paths["parent"], OVERLAP_TRANSACTION=paths["transaction"],
                STATE_PATH=paths["state"], OVERLAP_WORKFLOW_STATE=paths["workflow"], LEDGER_PATH=ledger,
                SOURCE_CONTROL_RECOVERY_TRANSACTION=paths["recovery"],
            ):
                m9_budget.verify_post_failure_immutable_runtime(runtime, {"state": "PREPARED"})
                paths["recovery"].write_text(json.dumps({"drift": True}), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "original recovery transaction drift"):
                    m9_budget.verify_post_failure_immutable_runtime(runtime, {"state": "PREPARED"})
                paths["recovery"].write_text(json.dumps({"name": "recovery"}), encoding="utf-8")
                paths["workflow"].write_text(json.dumps({"drift": True}), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "workflow_sha256"):
                    m9_budget.verify_post_failure_immutable_runtime(runtime)

    def test_source_control_retired_suffix_is_not_active_capability(self) -> None:
        self.assertTrue(".retired.json".endswith(".retired.json"))
        self.assertNotEqual("x.retired.json", "x.json")

    def test_source_control_product_closed_set_includes_staging_only(self) -> None:
        self.assertIn(m9_budget.LINUX_ROOT / "software/openmx-overlap-build.staging", m9_budget.SOURCE_RECOVERY_PRODUCTS)
        self.assertNotIn(m9_budget.LINUX_ROOT / "software/overlap-only-OpenMX", m9_budget.SOURCE_RECOVERY_PRODUCTS)
        self.assertNotIn(m9_budget.LINUX_ROOT / "software/DeepH-pack", m9_budget.SOURCE_RECOVERY_PRODUCTS)

    def test_process_receipt_requires_exact_pid_identity(self) -> None:
        receipt = {"pid": 7, "pgid": 7, "starttime_ticks": 11, "cmdline_sha256": "a" * 64}
        with mock.patch.object(m9_budget, "process_receipt", return_value=receipt):
            self.assertTrue(m9_budget.process_matches_receipt(receipt))
        altered = dict(receipt, starttime_ticks=12)
        with mock.patch.object(m9_budget, "process_receipt", return_value=receipt):
            self.assertFalse(m9_budget.process_matches_receipt(altered))

    def test_source_control_resume_rejects_parent_snapshot_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tx = root / "tx.json"
            snapshot = root / "parent.json"
            tx.write_text(json.dumps({"transaction_id": "parent"}), encoding="utf-8")
            snapshot.write_text("different", encoding="utf-8")
            recovery = {
                "state": "PREPARED",
                "parent_transaction_id": "parent",
                "parent_transaction_sha256": hashlib.sha256(tx.read_bytes()).hexdigest(),
                "parent_snapshot_sha256": "0" * 64,
                "parent_snapshot_bytes": 1,
                "retired_capability_path": str(root / "retired.json"),
                "stale_capability_path": str(root / "stale.json"),
            }
            with mock.patch.multiple(m9_budget, OVERLAP_TRANSACTION=tx, SOURCE_CONTROL_RECOVERY_PARENT=snapshot), \
                 mock.patch.object(m9_budget, "source_control_hard_stop") as hard_stop:
                self.assertEqual(m9_budget.source_control_resume(recovery, {}, {}), 125)
                hard_stop.assert_called_once()

    def test_source_control_resume_completes_state_first_half_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tx = root / "tx.json"; parent = root / "parent.json"; state_path = root / "state.json"
            workflow_path = root / "workflow.json"; ledger = root / "ledger.jsonl"; retired = root / "cap.retired.json"
            tx_bytes = json.dumps({"transaction_id": "parent", "state": "FAILED_COMMITTED"}).encode()
            tx.write_bytes(tx_bytes); parent.write_bytes(tx_bytes); ledger.write_text("", encoding="utf-8")
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                os.chown(ledger, 1000, 1000)
            retired.write_text("cap", encoding="utf-8")
            state_path.write_text(json.dumps({"hard_stopped": False, "active_overlap_transaction": None, "recovered_from_source_prepare_control_failure": "parent"}), encoding="utf-8")
            workflow_path.write_text(json.dumps({"schema_version": "m9-overlap-workflow-state-v1", "hard_stopped": True, "stage": "HARD_STOP", "active_transaction": None}), encoding="utf-8")
            receipt = {"path": retired.as_posix(), "bytes": 3, "sha256": hashlib.sha256(b"cap").hexdigest(), "uid": 1000, "gid": 1000, "mode": 0o600}
            event = {"event_id": "r:event", "event": "RECOVER", "transaction_id": "r", "parent_transaction_id": "parent"}
            bootstrap = {"python_executable": "/frozen/python"}; gate_receipt = {"gate_sha256": "g" * 64}
            recovery = {"schema_version": "m9-source-control-recovery-v1", "state": "SUCCESS_PENDING_COMMIT", "parent_transaction_id": "parent", "parent_transaction_sha256": hashlib.sha256(tx_bytes).hexdigest(), "parent_snapshot_sha256": hashlib.sha256(tx_bytes).hexdigest(), "parent_snapshot_bytes": len(tx_bytes), "parent_state_sha256": hashlib.sha256(state_path.read_bytes()).hexdigest(), "parent_workflow_sha256": hashlib.sha256(workflow_path.read_bytes()).hexdigest(), "parent_ledger_sha256": hashlib.sha256(b"").hexdigest(), "parent_ledger_bytes": 0, "parent_ledger_event_hashes": {}, "retired_capability_path": retired.as_posix(), "stale_capability_path": str(root / "cap.json"), "stale_capability_before": receipt, "event": event, "python_bootstrap": bootstrap, "gate_receipt": gate_receipt}
            recovery_path = root / "recovery.json"
            with mock.patch.multiple(m9_budget, OVERLAP_TRANSACTION=tx, SOURCE_CONTROL_RECOVERY_TRANSACTION=recovery_path, SOURCE_CONTROL_RECOVERY_PARENT=parent, STATE_PATH=state_path, OVERLAP_WORKFLOW_STATE=workflow_path, LEDGER_PATH=ledger), mock.patch.object(m9_budget, "file_stat_receipt", return_value=receipt):
                self.assertEqual(m9_budget.source_control_resume(recovery, bootstrap, gate_receipt), 0)
            self.assertFalse(json.loads(workflow_path.read_text(encoding="utf-8"))["hard_stopped"])
            self.assertEqual(recovery["state"], "SUCCESS_COMMITTED")

    def test_source_control_terminal_corrupt_ledger_is_hard_stopped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); tx = root / "tx.json"; parent = root / "parent.json"; ledger = root / "ledger.jsonl"
            tx_bytes = json.dumps({"transaction_id": "parent"}).encode(); tx.write_bytes(tx_bytes); parent.write_bytes(tx_bytes); ledger.write_text("not-json\n", encoding="utf-8")
            event = {"event_id": "r:event", "event": "RECOVER", "transaction_id": "r", "parent_transaction_id": "parent"}
            bootstrap = {"python_executable": "/frozen/python"}; gate_receipt = {"gate_sha256": "g" * 64}
            recovery = {"schema_version": "m9-source-control-recovery-v1", "state": "SUCCESS_COMMITTED", "parent_transaction_id": "parent", "parent_transaction_sha256": hashlib.sha256(tx_bytes).hexdigest(), "parent_snapshot_sha256": hashlib.sha256(tx_bytes).hexdigest(), "parent_snapshot_bytes": len(tx_bytes), "parent_ledger_sha256": hashlib.sha256(b"not-json\n").hexdigest(), "parent_ledger_bytes": len(b"not-json\n"), "parent_ledger_event_hashes": {}, "retired_capability_path": str(root / "retired.json"), "stale_capability_path": str(root / "cap.json"), "event": event, "python_bootstrap": bootstrap, "gate_receipt": gate_receipt}
            with mock.patch.multiple(m9_budget, OVERLAP_TRANSACTION=tx, SOURCE_CONTROL_RECOVERY_PARENT=parent, LEDGER_PATH=ledger), mock.patch.object(m9_budget, "source_control_hard_stop") as hard_stop:
                self.assertEqual(m9_budget.source_control_resume(recovery, bootstrap, gate_receipt), 125)
                hard_stop.assert_called_once()

    def test_source_control_verdict_domain_and_frozen_boundary(self) -> None:
        def build(root: Path, schema: str, decision: str, report_parent: Path | None = None):
            audits = root / "audits"
            controls = root / "controls"
            audits.mkdir()
            controls.mkdir()
            script = controls / "controller.py"
            test = controls / "test_controller.py"
            auth = root / "authorization.md"
            script.write_text("VALUE = 1\n", encoding="utf-8")
            test.write_text("VALUE = 2\n", encoding="utf-8")
            auth.write_text("authorized\n", encoding="utf-8")
            report_directory = audits if report_parent is None else report_parent
            report_directory.mkdir(exist_ok=True)
            report = report_directory / "verdict.json"
            report.write_text(
                json.dumps(
                    {
                        "schema_version": schema,
                        "decision_id": decision,
                        "verdict": "PASS",
                        "blocking": 0,
                        "non_blocking": 0,
                    }
                ),
                encoding="utf-8",
            )
            frozen = root / "frozen.json"
            files = {
                script.as_posix(): hashlib.sha256(script.read_bytes()).hexdigest(),
                test.as_posix(): hashlib.sha256(test.read_bytes()).hexdigest(),
                auth.as_posix(): hashlib.sha256(auth.read_bytes()).hexdigest(),
            }
            frozen.write_text(json.dumps({"files": files}), encoding="utf-8")
            gate_path = root / "gate.json"
            gate = {
                "schema_version": "m9-source-control-recovery-gate-v1",
                "status": "PASS",
                "blocking": 0,
                "non_blocking": 0,
                "decision_id": "D-017-source-control-recovery-v1",
                "audit_report_path": report.as_posix(),
                "audit_report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                "authorization_record_path": auth.as_posix(),
                "authorization_record_sha256": hashlib.sha256(auth.read_bytes()).hexdigest(),
                "frozen_hashes_path": frozen.as_posix(),
                "frozen_hashes_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
                "expected_failed_transaction": {"transaction_id": "parent"},
                "expected_stale_capability": {"capability_id": "cap"},
            }
            gate_path.write_text(json.dumps(gate), encoding="utf-8")
            return audits, controls, script, auth, report, frozen, gate_path, set(map(Path, files))

        for schema, decision in (
            ("m9-source-control-test-cleanup-audit-verdict-v1", "D-017-source-control-recovery-v1"),
            ("m9-source-control-recovery-audit-verdict-v1", "D-017-source-control-test-cleanup-v1"),
        ):
            with self.subTest(schema=schema, decision=decision), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                audits, controls, _, auth, _, frozen, gate_path, files = build(root, schema, decision)
                with mock.patch.multiple(
                    m9_budget,
                    AUDITS=audits,
                    OVERLAP_CONTROL_DIRECTORY=controls,
                    SOURCE_CONTROL_RECOVERY_GATE=gate_path,
                    SOURCE_CONTROL_RECOVERY_AUTHORIZATION=auth,
                    SOURCE_CONTROL_RECOVERY_FROZEN_HASHES=frozen,
                    SOURCE_RECOVERY_CONTROL_FILES=files,
                ):
                    with self.assertRaisesRegex(SystemExit, "structured PASS verdict"):
                        m9_budget.verify_source_control_recovery_gate_and_hashes()

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            audits, controls, script, auth, _, frozen, gate_path, files = build(
                root,
                "m9-source-control-recovery-audit-verdict-v1",
                "D-017-source-control-recovery-v1",
            )
            patcher = mock.patch.multiple(
                m9_budget,
                AUDITS=audits,
                OVERLAP_CONTROL_DIRECTORY=controls,
                SOURCE_CONTROL_RECOVERY_GATE=gate_path,
                SOURCE_CONTROL_RECOVERY_AUTHORIZATION=auth,
                SOURCE_CONTROL_RECOVERY_FROZEN_HASHES=frozen,
                SOURCE_RECOVERY_CONTROL_FILES=files,
            )
            with patcher:
                self.assertEqual(
                    m9_budget.verify_source_control_recovery_gate_and_hashes()["decision_id"],
                    "D-017-source-control-recovery-v1",
                )
                auth.write_text("drift\n", encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "authorization binding"):
                    m9_budget.verify_source_control_recovery_gate_and_hashes()
                auth.write_text("authorized\n", encoding="utf-8")
                script.write_text("VALUE = 3\n", encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "frozen file mismatch"):
                    m9_budget.verify_source_control_recovery_gate_and_hashes()
                script.write_text("VALUE = 1\n", encoding="utf-8")
                (controls / "__pycache__").mkdir()
                with self.assertRaisesRegex(SystemExit, "cache, symlink, or subdirectory"):
                    m9_budget.verify_source_control_recovery_gate_and_hashes()

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root / "outside"
            audits, controls, _, auth, _, frozen, gate_path, files = build(
                root,
                "m9-source-control-recovery-audit-verdict-v1",
                "D-017-source-control-recovery-v1",
                outside,
            )
            with mock.patch.multiple(
                m9_budget,
                AUDITS=audits,
                OVERLAP_CONTROL_DIRECTORY=controls,
                SOURCE_CONTROL_RECOVERY_GATE=gate_path,
                SOURCE_CONTROL_RECOVERY_AUTHORIZATION=auth,
                SOURCE_CONTROL_RECOVERY_FROZEN_HASHES=frozen,
                SOURCE_RECOVERY_CONTROL_FILES=files,
            ):
                with self.assertRaisesRegex(SystemExit, "directly under 08_audits"):
                    m9_budget.verify_source_control_recovery_gate_and_hashes()

    def test_source_control_bootstrap_precedes_gate_and_state(self) -> None:
        verifier = mock.Mock()
        with mock.patch.object(m9_budget.os, "geteuid", return_value=0), \
             mock.patch.object(
                 m9_budget,
                 "isolated_bootstrap_provenance",
                 side_effect=SystemExit("formal overlap entry requires frozen Python with -I -S -B"),
             ), \
             mock.patch.object(m9_budget, "verify_source_control_recovery_gate_and_hashes", verifier):
            with self.assertRaisesRegex(SystemExit, "-I -S -B"):
                m9_budget.command_overlap_recover_source_control_failure(mock.Mock())
        verifier.assert_not_called()

        script = SCRIPTS / "m9_budget.py"
        formal = [
            m9_budget.SOURCE_CONTROL_RECOVERY_TRANSACTION,
            m9_budget.SOURCE_CONTROL_RECOVERY_PARENT,
        ]
        before = self.file_bytes(formal)
        gate_before = os.lstat(m9_budget.SOURCE_CONTROL_RECOVERY_GATE)
        with tempfile.TemporaryDirectory() as temporary:
            wrapper = Path(temporary) / "bootstrap_probe.py"
            wrapper.write_text(
                "import importlib.util\n"
                f"spec=importlib.util.spec_from_file_location('budget_probe',{script.as_posix()!r})\n"
                "module=importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(module)\n"
                "module.isolated_bootstrap_provenance()\n",
                encoding="utf-8",
            )
            candidates = [
                [Path("/usr/bin/python3.10"), "-I", "-S", "-B"],
                [Path(sys.executable), "-I", "-B"],
            ]
            for prefix in candidates:
                if not prefix[0].is_file():
                    continue
                result = subprocess.run(
                    [prefix[0].as_posix(), *prefix[1:], wrapper.as_posix()],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(
                    b"requires frozen Python" in result.stderr or b"-I -S -B" in result.stderr,
                    result.stderr.decode("utf-8", errors="replace"),
                )
        self.assertEqual(self.file_bytes(formal), before)
        gate_after = os.lstat(m9_budget.SOURCE_CONTROL_RECOVERY_GATE)
        self.assertEqual(
            (gate_after.st_dev, gate_after.st_ino, gate_after.st_size, gate_after.st_mtime_ns),
            (gate_before.st_dev, gate_before.st_ino, gate_before.st_size, gate_before.st_mtime_ns),
        )


    def test_source_control_first_success_all_crash_windows_and_terminal_replay(self) -> None:
        stages = (
            "parent_snapshot", "prepared", "capability_rename", "capability_retired",
            "success_pending", "ledger_append", "ledger_phase", "state_write",
            "state_phase", "workflow_write", "terminal",
        )

        def normalize(value, root: Path):
            if isinstance(value, dict):
                return {key: normalize(item, root) for key, item in value.items()}
            if isinstance(value, list):
                return [normalize(item, root) for item in value]
            if isinstance(value, str):
                return value.replace(root.as_posix(), "<TEMP_ROOT>")
            return value

        def structure(value):
            if isinstance(value, dict):
                return {key: structure(item) for key, item in value.items()}
            if isinstance(value, list):
                return [structure(item) for item in value]
            return type(value).__name__

        def run_case(root: Path, stage: str | None) -> dict:
            with self.source_recovery_tree(root) as fixture:
                paths = fixture["paths"]
                real_atomic = m9_budget.atomic_owned_json
                real_append = m9_budget.append_event_once
                real_replace = os.replace
                fired = False

                def interrupt() -> None:
                    nonlocal fired
                    if not fired:
                        fired = True
                        raise KeyboardInterrupt(stage)

                def atomic(path: Path, value: dict) -> None:
                    real_atomic(path, value)
                    checks = {
                        "prepared": path == paths["recovery"] and value.get("state") == "PREPARED",
                        "capability_retired": path == paths["recovery"] and value.get("state") == "CAPABILITY_RETIRED",
                        "success_pending": path == paths["recovery"] and value.get("state") == "SUCCESS_PENDING_COMMIT" and "ledger_phase" not in value,
                        "ledger_phase": path == paths["recovery"] and value.get("ledger_phase") == "COMMITTED",
                        "state_write": path == paths["state"],
                        "state_phase": path == paths["recovery"] and value.get("state_commit_phase") == "STATE_COMMITTED",
                        "workflow_write": path == paths["workflow"],
                        "terminal": path == paths["recovery"] and value.get("state") == "SUCCESS_COMMITTED",
                    }
                    if checks.get(stage, False):
                        interrupt()

                def append(event: dict, **kwargs) -> None:
                    real_append(event, **kwargs)
                    if stage == "ledger_append":
                        interrupt()

                def replace(src, dst) -> None:
                    real_replace(src, dst)
                    if stage == "parent_snapshot" and Path(dst) == paths["parent"]:
                        interrupt()
                    if stage == "capability_rename" and Path(src) == fixture["capability"]:
                        interrupt()

                if stage is not None:
                    with mock.patch.object(m9_budget, "atomic_owned_json", side_effect=atomic), \
                         mock.patch.object(m9_budget, "append_event_once", side_effect=append), \
                         mock.patch.object(m9_budget.os, "replace", side_effect=replace):
                        with self.assertRaises(KeyboardInterrupt):
                            m9_budget.command_overlap_recover_source_control_failure(mock.Mock())
                    self.assertTrue(fired, stage)

                self.assertEqual(m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 0)
                recovery = json.loads(paths["recovery"].read_text(encoding="utf-8"))
                self.assertEqual(recovery["state"], "SUCCESS_COMMITTED")
                self.assertEqual(recovery["python_bootstrap"], fixture["bootstrap"])
                self.assertEqual(recovery["gate_receipt"]["decision_id"], "D-017-source-control-recovery-v1")
                self.assertFalse(fixture["capability"].exists())
                retired = Path(recovery["retired_capability_path"])
                self.assertTrue(retired.is_file())
                self.assertEqual(
                    sum(key.endswith(":source-control-recovery") for key in m9_budget.ledger_event_ids()),
                    1,
                )
                observed = [paths["state"], paths["workflow"], paths["transaction"], paths["ledger"], paths["recovery"], paths["parent"], retired]
                before_replay = self.file_bytes(observed)
                self.assertEqual(m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 0)
                self.assertEqual(self.file_bytes(observed), before_replay)
                return normalize(recovery, root)

        with tempfile.TemporaryDirectory() as temporary:
            baseline = run_case(Path(temporary), None)
        for stage in stages:
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as temporary:
                resumed = run_case(Path(temporary), stage)
                self.assertEqual(structure(resumed), structure(baseline))

    def test_source_control_recovery_opens_existing_lock_without_create(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.source_recovery_tree(Path(temporary)) as fixture:
                original_open = Path.open
                lock_modes = []

                def guarded_open(path: Path, mode="r", *args, **kwargs):
                    if path == fixture["paths"]["lock"]:
                        lock_modes.append(mode)
                        if mode == "a+":
                            raise PermissionError("protected_regular rejects O_CREAT on the existing lock")
                    return original_open(path, mode, *args, **kwargs)

                with mock.patch.object(Path, "open", new=guarded_open):
                    self.assertEqual(m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 0)
                self.assertEqual(lock_modes, ["r+"])

    def test_post_failure_migration_resumes_same_transaction_and_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.source_recovery_tree(root) as fixture:
                paths = fixture["paths"]
                old_gate = {
                    "schema_version": "m9-source-control-recovery-gate-v1",
                    "status": "PASS", "blocking": 0, "non_blocking": 0,
                    "decision_id": "D-017-source-control-recovery-v1",
                    "audit_report_path": "/audit/old.json",
                    "audit_report_sha256": "1" * 64,
                    "authorization_record_path": "/audit/auth.md",
                    "authorization_record_sha256": "2" * 64,
                    "frozen_hashes_path": "/audit/frozen.json",
                    "frozen_hashes_sha256": "3" * 64,
                    "expected_failed_transaction": {"transaction_id": "parent-source-prepare"},
                    "expected_stale_capability": {"capability_id": "1" * 32},
                }
                paths["gate"].write_text(json.dumps(old_gate), encoding="utf-8")
                with mock.patch.object(
                    m9_budget, "append_event_once", side_effect=PermissionError("protected_regular")
                ):
                    self.assertEqual(
                        m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 125
                    )
                failed = json.loads(paths["recovery"].read_text(encoding="utf-8"))
                self.assertEqual(failed["state"], "FAILED_COMMITTED")
                original_txid = failed["transaction_id"]
                original_event_id = failed["event"]["event_id"]
                retired_capability = Path(failed["retired_capability_path"])
                runtime = {
                    "recovery_transaction_sha256": hashlib.sha256(paths["recovery"].read_bytes()).hexdigest(),
                    "recovery_transaction_id": original_txid,
                    "recovery_event_id": original_event_id,
                    "parent_snapshot_sha256": hashlib.sha256(paths["parent"].read_bytes()).hexdigest(),
                    "parent_transaction_sha256": hashlib.sha256(paths["transaction"].read_bytes()).hexdigest(),
                    "state_sha256": hashlib.sha256(paths["state"].read_bytes()).hexdigest(),
                    "workflow_sha256": hashlib.sha256(paths["workflow"].read_bytes()).hexdigest(),
                    "ledger_sha256": hashlib.sha256(paths["ledger"].read_bytes()).hexdigest(),
                    "recovery_event_count": 0,
                    "retired_capability_path": retired_capability.as_posix(),
                    "retired_capability_sha256": hashlib.sha256(retired_capability.read_bytes()).hexdigest(),
                    "active_gate_sha256": hashlib.sha256(paths["gate"].read_bytes()).hexdigest(),
                }
                post_journal = root / "root-control" / "post-failure.json"
                snapshot = root / "root-control" / "failed-original.json"
                retired_gate = root / "manifests" / "gate.pre-ledger-fix.retired.json"
                post_journal.parent.mkdir()
                verdict_path = root / "migration-verdict.json"
                replacement_path = root / "replacement-verdict.json"
                frozen_path = root / "frozen.json"
                auth_path = root / "authorization.md"
                for path, payload in (
                    (verdict_path, b"{}"), (replacement_path, b"{}"),
                    (frozen_path, b"{}"), (auth_path, b"authorized"),
                ):
                    path.write_bytes(payload)

                def receipt(path: Path) -> dict[str, object]:
                    current = os.lstat(path)
                    return {
                        "path": path.as_posix(), "bytes": current.st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "uid": current.st_uid, "gid": current.st_gid,
                        "mode": stat.S_IMODE(current.st_mode), "nlink": current.st_nlink,
                    }

                def relaxed_json(path: Path):
                    return receipt(path), json.loads(path.read_text(encoding="utf-8"))

                def root_bytes(path: Path, payload: bytes) -> None:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload)
                    path.chmod(0o600)

                def root_json(path: Path, value: dict) -> None:
                    root_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

                replacement_verdict = {
                    "schema_version": "m9-source-control-recovery-audit-verdict-v1",
                    "decision_id": "D-017-source-control-recovery-v1",
                    "verdict": "PASS", "blocking": 0, "non_blocking": 0,
                }
                bindings = {
                    "verdict": receipt(verdict_path),
                    "replacement_verdict": receipt(replacement_path),
                    "frozen": receipt(frozen_path),
                    "contract": receipt(frozen_path),
                    "authorization_sha256": hashlib.sha256(auth_path.read_bytes()).hexdigest(),
                    "runtime": runtime,
                }
                verdict = {
                    "decision_id": "D-017-source-control-post-failure-migration-v1"
                }
                patches = {
                    "SOURCE_CONTROL_POST_FAILURE_JOURNAL": post_journal,
                    "SOURCE_CONTROL_FAILED_RECOVERY_SNAPSHOT": snapshot,
                    "SOURCE_CONTROL_GATE_PRE_LEDGER_FIX_RETIRED": retired_gate,
                    "SOURCE_CONTROL_POST_FAILURE_MIGRATION_VERDICT": verdict_path,
                    "SOURCE_CONTROL_POST_FAILURE_REPLACEMENT_VERDICT": replacement_path,
                    "SOURCE_CONTROL_RECOVERY_FROZEN_HASHES": frozen_path,
                    "SOURCE_CONTROL_RECOVERY_AUTHORIZATION": auth_path,
                }
                with mock.patch.multiple(m9_budget, **patches), \
                     mock.patch.object(m9_budget, "verify_source_control_post_failure_migration", return_value=(verdict, replacement_verdict, bindings)), \
                     mock.patch.object(m9_budget, "strict_root_private_json", side_effect=relaxed_json), \
                     mock.patch.object(m9_budget, "strict_root_private_receipt", side_effect=receipt), \
                     mock.patch.object(m9_budget, "atomic_root_private_bytes", side_effect=root_bytes), \
                     mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=root_json), \
                     mock.patch.object(m9_budget, "verify_source_control_recovery_gate_and_hashes", side_effect=lambda: json.loads(paths["gate"].read_text(encoding="utf-8"))):
                    self.assertEqual(
                        m9_budget.command_migrate_source_control_post_failure(mock.Mock()), 0
                    )
                    migrated = json.loads(paths["recovery"].read_text(encoding="utf-8"))
                    self.assertEqual(migrated["transaction_id"], original_txid)
                    self.assertEqual(migrated["event"]["event_id"], original_event_id)
                    self.assertEqual(migrated["state"], "FAILED_COMMITTED")
                    self.assertEqual(
                        m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 0
                    )
                    completed = json.loads(paths["recovery"].read_text(encoding="utf-8"))
                    self.assertEqual(completed["state"], "SUCCESS_COMMITTED")
                    self.assertEqual(completed["transaction_id"], original_txid)
                    self.assertEqual(completed["event"]["event_id"], original_event_id)
                    self.assertEqual(
                        sum(key == original_event_id for key in m9_budget.ledger_event_ids()), 1
                    )
                    observed = [paths["recovery"], paths["state"], paths["workflow"], paths["ledger"], post_journal, snapshot, retired_gate, paths["gate"]]
                    before = self.file_bytes(observed)
                    self.assertEqual(
                        m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 0
                    )
                    self.assertEqual(self.file_bytes(observed), before)

    def test_source_control_drift_matrix_is_hard_stopped(self) -> None:
        def prepare(root: Path):
            manager = self.source_recovery_tree(root)
            fixture = manager.__enter__()
            paths = fixture["paths"]
            real_atomic = m9_budget.atomic_owned_json

            def stop_after_prepared(path: Path, value: dict) -> None:
                real_atomic(path, value)
                if path == paths["recovery"] and value.get("state") == "PREPARED":
                    raise KeyboardInterrupt("PREPARED")

            with mock.patch.object(m9_budget, "atomic_owned_json", side_effect=stop_after_prepared):
                with self.assertRaises(KeyboardInterrupt):
                    m9_budget.command_overlap_recover_source_control_failure(mock.Mock())
            return manager, fixture

        drift_cases = ("parent_transaction", "parent_ledger_extra", "same_id_other_payload", "ledger_order", "state", "workflow", "bootstrap", "gate")
        for drift in drift_cases:
            with self.subTest(drift=drift), tempfile.TemporaryDirectory() as temporary:
                manager, fixture = prepare(Path(temporary))
                try:
                    paths = fixture["paths"]
                    recovery = json.loads(paths["recovery"].read_text(encoding="utf-8"))
                    if drift == "parent_transaction":
                        paths["transaction"].write_text(json.dumps({"transaction_id": "drift"}), encoding="utf-8")
                    elif drift == "parent_ledger_extra":
                        with paths["ledger"].open("a", encoding="utf-8") as handle:
                            handle.write(json.dumps({"event_id": "extra", "event": "DRIFT"}) + "\n")
                    elif drift == "same_id_other_payload":
                        wrong = dict(recovery["event"], event="WRONG")
                        with paths["ledger"].open("a", encoding="utf-8") as handle:
                            handle.write(json.dumps(wrong, sort_keys=True) + "\n")
                    elif drift == "ledger_order":
                        lines = paths["ledger"].read_text(encoding="utf-8").splitlines(True)
                        paths["ledger"].write_text("".join(reversed(lines)), encoding="utf-8")
                    elif drift == "state":
                        value = json.loads(paths["state"].read_text(encoding="utf-8")); value["drift"] = True
                        paths["state"].write_text(json.dumps(value), encoding="utf-8")
                    elif drift == "workflow":
                        value = json.loads(paths["workflow"].read_text(encoding="utf-8")); value["drift"] = True
                        paths["workflow"].write_text(json.dumps(value), encoding="utf-8")
                    elif drift == "bootstrap":
                        recovery["python_bootstrap"] = {"python_executable": "/wrong"}
                        paths["recovery"].write_text(json.dumps(recovery), encoding="utf-8")
                    elif drift == "gate":
                        recovery["gate_receipt"]["decision_id"] = "wrong"
                        paths["recovery"].write_text(json.dumps(recovery), encoding="utf-8")
                    self.assertEqual(m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 125)
                    self.assertTrue(json.loads(paths["state"].read_text(encoding="utf-8"))["hard_stopped"])
                    self.assertTrue(json.loads(paths["workflow"].read_text(encoding="utf-8"))["hard_stopped"])
                    self.assertEqual(json.loads(paths["recovery"].read_text(encoding="utf-8"))["state"], "FAILED_COMMITTED")
                finally:
                    manager.__exit__(None, None, None)

        for drift in ("state", "workflow", "ledger"):
            with self.subTest(terminal_drift=drift), tempfile.TemporaryDirectory() as temporary:
                with self.source_recovery_tree(Path(temporary)) as fixture:
                    paths = fixture["paths"]
                    self.assertEqual(m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 0)
                    with paths[drift].open("ab") as handle:
                        handle.write(b" \n" if drift != "ledger" else b'{"event_id":"extra","event":"DRIFT"}\n')
                    self.assertEqual(m9_budget.command_overlap_recover_source_control_failure(mock.Mock()), 125)
                    self.assertTrue(json.loads(paths["state"].read_text(encoding="utf-8"))["hard_stopped"])

    def test_source_control_retired_is_unconsumable_and_new_capability_is_one_shot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            capability_id = "2" * 32
            (root / f"{capability_id}.retired.json").write_text("{}", encoding="utf-8")
            with mock.patch.object(m9_overlap_source_launcher, "CAPABILITY_ROOT", root), \
                 mock.patch.object(m9_overlap_source_launcher.time, "monotonic", side_effect=[0.0, 11.0]), \
                 mock.patch.object(m9_overlap_source_launcher.time, "sleep", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "was not issued"):
                    m9_overlap_source_launcher.wait_and_consume_capability(capability_id)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            capability_id = "3" * 32
            parent_pid = os.getppid()
            parent_argv = [item.decode("utf-8") for item in Path(f"/proc/{parent_pid}/cmdline").read_bytes().split(b"\0") if item]
            launcher_argv = [Path(sys.executable).resolve().as_posix(), "-I", "-S", "-B", Path(m9_overlap_source_launcher.__file__).resolve().as_posix(), "--capability-id", capability_id]
            capability = {
                "schema_version": "m9-overlap-capability-v1", "state": "BOUND",
                "capability_id": capability_id, "transaction_id": "new-source-prepare",
                "child_pid": os.getpid(), "budget_pid": parent_pid,
                "budget_argv": parent_argv, "launcher_argv": launcher_argv,
                "action": "source_prepare",
            }
            path = root / f"{capability_id}.json"
            path.write_text(json.dumps(capability), encoding="utf-8"); path.chmod(0o600)
            with mock.patch.object(m9_overlap_source_launcher, "CAPABILITY_ROOT", root):
                consumed = m9_overlap_source_launcher.wait_and_consume_capability(capability_id)
                self.assertEqual(consumed["state"], "CONSUMED")
                self.assertEqual(json.loads((root / f"{capability_id}.consumed.json").read_text(encoding="utf-8"))["state"], "CONSUMED")
                self.assertFalse(path.exists())
                with self.assertRaisesRegex(RuntimeError, "was not issued"):
                    m9_overlap_source_launcher.wait_and_consume_capability(capability_id)

    def test_invalid_source_gate_disposition_crash_matrix_and_terminal_replay(self) -> None:
        stages = ("prepared", "rename", "retired_journal", "replacement", "replacement_journal", "terminal")

        def run(root: Path, stage: str | None) -> dict:
            with self.source_gate_disposition_tree(root) as fixture:
                real_json = m9_budget.atomic_root_private_json
                real_bytes = m9_budget.atomic_root_private_bytes
                real_replace = os.replace
                fired = False

                def interrupt() -> None:
                    nonlocal fired
                    if not fired:
                        fired = True
                        raise KeyboardInterrupt(stage)

                def write_json(path: Path, value: dict) -> None:
                    real_json(path, value)
                    if path == fixture["journal"]:
                        if stage == "prepared" and value.get("state") == "PREPARED": interrupt()
                        if stage == "retired_journal" and value.get("state") == "INVALID_GATE_RETIRED": interrupt()
                        if stage == "replacement_journal" and value.get("state") == "REPLACEMENT_CREATED": interrupt()
                        if stage == "terminal" and value.get("state") == "SUCCESS_COMMITTED": interrupt()

                def write_bytes(path: Path, payload: bytes) -> None:
                    real_bytes(path, payload)
                    if stage == "replacement" and path == fixture["active"]: interrupt()

                def replace(src, dst) -> None:
                    real_replace(src, dst)
                    if stage == "rename" and Path(dst) == fixture["retired"]: interrupt()

                if stage is not None:
                    with mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=write_json), \
                         mock.patch.object(m9_budget, "atomic_root_private_bytes", side_effect=write_bytes), \
                         mock.patch.object(m9_budget.os, "replace", side_effect=replace):
                        with self.assertRaises(KeyboardInterrupt):
                            m9_budget.command_dispose_invalid_source_control_gate(mock.Mock())
                    self.assertTrue(fired)
                self.assertEqual(m9_budget.command_dispose_invalid_source_control_gate(mock.Mock()), 0)
                journal = json.loads(fixture["journal"].read_text(encoding="utf-8"))
                self.assertEqual(journal["state"], "SUCCESS_COMMITTED")
                self.assertTrue(fixture["active"].is_file())
                self.assertTrue(fixture["retired"].is_file())
                observed = [fixture["active"], fixture["retired"], fixture["journal"]]
                before = self.file_bytes(observed)
                self.assertEqual(m9_budget.command_dispose_invalid_source_control_gate(mock.Mock()), 0)
                self.assertEqual(self.file_bytes(observed), before)
                return {key: type(value).__name__ for key, value in journal.items()}

        with tempfile.TemporaryDirectory() as temporary:
            baseline = run(Path(temporary), None)
        for stage in stages:
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as temporary:
                self.assertEqual(run(Path(temporary), stage), baseline)

    def test_invalid_source_gate_disposition_rejects_runtime_drift_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.source_gate_disposition_tree(Path(temporary)) as fixture:
                before = self.file_bytes([fixture["active"], fixture["retired"], fixture["journal"]])
                with mock.patch.object(
                    m9_budget,
                    "source_control_disposition_runtime_receipt",
                    return_value={"state_sha256": "drift"},
                ):
                    with self.assertRaisesRegex(SystemExit, "runtime drift"):
                        m9_budget.command_dispose_invalid_source_control_gate(mock.Mock())
                self.assertEqual(self.file_bytes([fixture["active"], fixture["retired"], fixture["journal"]]), before)

    def test_invalid_source_gate_disposition_opens_existing_lock_without_create(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.source_gate_disposition_tree(Path(temporary)) as fixture:
                original_open = Path.open
                lock_modes = []

                def guarded_open(path: Path, mode="r", *args, **kwargs):
                    if path == fixture["lock"]:
                        lock_modes.append(mode)
                        if mode == "a+":
                            raise PermissionError("protected_regular rejects O_CREAT on the existing lock")
                    return original_open(path, mode, *args, **kwargs)

                with mock.patch.object(Path, "open", new=guarded_open):
                    self.assertEqual(m9_budget.command_dispose_invalid_source_control_gate(mock.Mock()), 0)
                self.assertEqual(lock_modes, ["r+"])

    def test_invalid_source_gate_disposition_rejects_journal_state_and_old_receipt_drift(self) -> None:
        for drift in ("state", "old_gate"):
            with self.subTest(drift=drift), tempfile.TemporaryDirectory() as temporary:
                with self.source_gate_disposition_tree(Path(temporary)) as fixture:
                    real_json = m9_budget.atomic_root_private_json
                    def stop_after_prepared(path: Path, value: dict) -> None:
                        real_json(path, value)
                        if path == fixture["journal"] and value.get("state") == "PREPARED":
                            raise KeyboardInterrupt("PREPARED")
                    with mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=stop_after_prepared):
                        with self.assertRaises(KeyboardInterrupt):
                            m9_budget.command_dispose_invalid_source_control_gate(mock.Mock())
                    journal = json.loads(fixture["journal"].read_text(encoding="utf-8"))
                    if drift == "state":
                        journal["state"] = "UNKNOWN"
                    else:
                        journal["old_gate"]["sha256"] = "0" * 64
                    fixture["journal"].write_text(json.dumps(journal), encoding="utf-8")
                    before = self.file_bytes([fixture["active"], fixture["retired"], fixture["journal"]])
                    with self.assertRaisesRegex(SystemExit, "journal state mismatch|old receipt drift"):
                        m9_budget.command_dispose_invalid_source_control_gate(mock.Mock())
                    self.assertEqual(self.file_bytes([fixture["active"], fixture["retired"], fixture["journal"]]), before)

    def test_invalid_source_gate_disposition_rejects_terminal_linked_journal_without_mutation(self) -> None:
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                with self.source_gate_disposition_tree(root) as fixture:
                    self.assertEqual(m9_budget.command_dispose_invalid_source_control_gate(mock.Mock()), 0)
                    journal_bytes = fixture["journal"].read_bytes()
                    active_bytes = fixture["active"].read_bytes()
                    retired_bytes = fixture["retired"].read_bytes()
                    sibling = root / f"journal-{kind}-sibling.json"
                    if kind == "symlink":
                        sibling.write_bytes(journal_bytes)
                        fixture["journal"].unlink()
                        fixture["journal"].symlink_to(sibling)
                    else:
                        os.link(fixture["journal"], sibling)

                    with self.assertRaisesRegex(
                        SystemExit,
                        "root-private control object is missing or not regular|root-private control object metadata mismatch",
                    ):
                        m9_budget.command_dispose_invalid_source_control_gate(mock.Mock())

                    self.assertEqual(fixture["active"].read_bytes(), active_bytes)
                    self.assertEqual(fixture["retired"].read_bytes(), retired_bytes)
                    self.assertEqual(fixture["journal"].read_bytes(), journal_bytes)
                    if kind == "symlink":
                        self.assertTrue(fixture["journal"].is_symlink())
                    else:
                        self.assertEqual(os.lstat(fixture["journal"]).st_nlink, 2)
                        self.assertEqual(sibling.read_bytes(), journal_bytes)

    def test_root_private_single_fd_read_rejects_link_swap_during_read(self) -> None:
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                path = root / "journal.json"
                sibling = root / "journal-sibling.json"
                payload = b'{"state":"SUCCESS_COMMITTED"}\n'
                path.write_bytes(payload)
                path.chmod(0o600)
                real_fstat = os.fstat
                real_lstat = os.lstat
                real_read = os.read
                injected = False

                def root_stat(value):
                    return argparse.Namespace(
                        st_dev=value.st_dev, st_ino=value.st_ino, st_mode=value.st_mode,
                        st_uid=0, st_gid=0, st_nlink=value.st_nlink, st_size=value.st_size,
                    )

                def mutate_then_read(descriptor: int, size: int) -> bytes:
                    nonlocal injected
                    if not injected:
                        injected = True
                        if kind == "symlink":
                            os.replace(path, sibling)
                            path.symlink_to(sibling)
                        else:
                            os.link(path, sibling)
                    return real_read(descriptor, size)

                with mock.patch.object(m9_budget.os, "fstat", side_effect=lambda fd: root_stat(real_fstat(fd))), \
                     mock.patch.object(m9_budget.os, "lstat", side_effect=lambda item: root_stat(real_lstat(item))), \
                     mock.patch.object(m9_budget.os, "read", side_effect=mutate_then_read):
                    with self.assertRaisesRegex(SystemExit, "path changed while reading"):
                        m9_budget.read_strict_root_private_bytes(path)
                self.assertTrue(injected)
                if kind == "symlink":
                    self.assertTrue(path.is_symlink())
                    self.assertEqual(sibling.read_bytes(), payload)
                else:
                    self.assertEqual(os.lstat(path).st_nlink, 2)
                    self.assertEqual(sibling.read_bytes(), payload)

    def test_source_gate_disposition_rejects_dangling_recovery_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dangling = root / "recovery.json"
            dangling.symlink_to(root / "missing-target.json")
            with mock.patch.multiple(
                m9_budget,
                SOURCE_CONTROL_RECOVERY_TRANSACTION=dangling,
                SOURCE_CONTROL_RECOVERY_PARENT=root / "missing-parent.json",
            ):
                with self.assertRaisesRegex(SystemExit, "requires absent recovery"):
                    m9_budget.source_control_disposition_runtime_receipt()

    def test_invalid_source_gate_disposition_verdict_is_domain_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); audits = root / "audits"; audits.mkdir()
            report = audits / "report.md"; report.write_text("PASS", encoding="utf-8")
            replacement_path = audits / "replacement.json"
            replacement_path.write_text(json.dumps({
                "schema_version": "m9-source-control-recovery-audit-verdict-v1",
                "decision_id": "D-017-source-control-recovery-v1",
                "verdict": "PASS", "blocking": 0, "non_blocking": 0,
            }), encoding="utf-8")
            controls = root / "controls"; controls.mkdir()
            controller = controls / "controller.py"; controller.write_text("VALUE = 1\n", encoding="utf-8")
            frozen = root / "frozen.json"
            frozen.write_text(json.dumps({"files": {
                controller.as_posix(): hashlib.sha256(controller.read_bytes()).hexdigest(),
            }}), encoding="utf-8")
            auth = root / "auth.md"; auth.write_text("authorized", encoding="utf-8")
            verdict_path = audits / "disposition.json"
            verdict = {
                "schema_version": "m9-source-control-gate-disposition-audit-verdict-v1",
                "decision_id": "D-017-source-control-gate-disposition-v1",
                "verdict": "PASS", "blocking": 0, "non_blocking": 0,
                "scope": "RETIRE_CLOSED_SET_INVALID_GATE_AND_CREATE_REPLACEMENT_ONLY",
                "old_gate_sha256": "a" * 64, "old_gate_bytes": 10,
                "report_path": report.as_posix(),
                "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                "replacement_verdict_path": replacement_path.as_posix(),
                "replacement_verdict_sha256": hashlib.sha256(replacement_path.read_bytes()).hexdigest(),
                "frozen_hashes_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
                "authorization_record_sha256": hashlib.sha256(auth.read_bytes()).hexdigest(),
            }
            verdict_path.write_text(json.dumps(verdict), encoding="utf-8")
            with mock.patch.multiple(
                m9_budget,
                AUDITS=audits,
                SOURCE_CONTROL_GATE_DISPOSITION_VERDICT=verdict_path,
                SOURCE_CONTROL_RECOVERY_REPLACEMENT_VERDICT=replacement_path,
                SOURCE_CONTROL_RECOVERY_FROZEN_HASHES=frozen,
                SOURCE_CONTROL_RECOVERY_AUTHORIZATION=auth,
                SOURCE_RECOVERY_CONTROL_FILES={controller},
                OVERLAP_CONTROL_DIRECTORY=controls,
                INVALID_SOURCE_CONTROL_GATE_SHA256="a" * 64,
                INVALID_SOURCE_CONTROL_GATE_BYTES=10,
            ):
                self.assertEqual(m9_budget.verify_source_control_gate_disposition()[0]["verdict"], "PASS")
                verdict["scope"] = "CREATE_SOURCE_CONTROL_RECOVERY_GATE_ONLY"
                verdict_path.write_text(json.dumps(verdict), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "exact zero-issue PASS"):
                    m9_budget.verify_source_control_gate_disposition()
                verdict["scope"] = "RETIRE_CLOSED_SET_INVALID_GATE_AND_CREATE_REPLACEMENT_ONLY"
                verdict_path.write_text(json.dumps(verdict), encoding="utf-8")
                controller.write_text("VALUE = 2\n", encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "frozen member mismatch"):
                    m9_budget.verify_source_control_gate_disposition()

    def test_source_control_gate_lock_refresh_crash_matrix_and_terminal_replay(self) -> None:
        stages = ("prepared", "rename", "retired_journal", "replacement", "replacement_journal", "terminal")

        def run(root: Path, stage: str | None) -> dict:
            with self.source_gate_lock_refresh_tree(root) as fixture:
                real_json = m9_budget.atomic_root_private_json
                real_bytes = m9_budget.atomic_root_private_bytes
                real_replace = os.replace
                fired = False

                def interrupt() -> None:
                    nonlocal fired
                    if not fired:
                        fired = True
                        raise KeyboardInterrupt(stage)

                def write_json(path: Path, value: dict) -> None:
                    real_json(path, value)
                    if path == fixture["refresh_journal"]:
                        if stage == "prepared" and value.get("state") == "PREPARED": interrupt()
                        if stage == "retired_journal" and value.get("state") == "OLD_GATE_RETIRED": interrupt()
                        if stage == "replacement_journal" and value.get("state") == "REPLACEMENT_CREATED": interrupt()
                        if stage == "terminal" and value.get("state") == "SUCCESS_COMMITTED": interrupt()

                def write_bytes(path: Path, payload: bytes) -> None:
                    real_bytes(path, payload)
                    if stage == "replacement" and path == fixture["active"]: interrupt()

                def replace(src, dst) -> None:
                    real_replace(src, dst)
                    if stage == "rename" and Path(dst) == fixture["pre_retired"]: interrupt()

                if stage is not None:
                    with mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=write_json), \
                         mock.patch.object(m9_budget, "atomic_root_private_bytes", side_effect=write_bytes), \
                         mock.patch.object(m9_budget.os, "replace", side_effect=replace):
                        with self.assertRaises(KeyboardInterrupt):
                            m9_budget.command_refresh_source_control_recovery_gate(mock.Mock())
                    self.assertTrue(fired)
                self.assertEqual(m9_budget.command_refresh_source_control_recovery_gate(mock.Mock()), 0)
                journal = json.loads(fixture["refresh_journal"].read_text(encoding="utf-8"))
                self.assertEqual(journal["state"], "SUCCESS_COMMITTED")
                self.assertTrue(fixture["active"].is_file())
                self.assertTrue(fixture["pre_retired"].is_file())
                observed = [fixture["active"], fixture["pre_retired"], fixture["refresh_journal"]]
                before = self.file_bytes(observed)
                self.assertEqual(m9_budget.command_refresh_source_control_recovery_gate(mock.Mock()), 0)
                self.assertEqual(self.file_bytes(observed), before)
                return {key: type(value).__name__ for key, value in journal.items()}

        with tempfile.TemporaryDirectory() as temporary:
            baseline = run(Path(temporary), None)
        for stage in stages:
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as temporary:
                self.assertEqual(run(Path(temporary), stage), baseline)

    def test_source_control_gate_lock_refresh_opens_existing_lock_without_create(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.source_gate_lock_refresh_tree(Path(temporary)) as fixture:
                original_open = Path.open
                lock_modes = []

                def guarded_open(path: Path, mode="r", *args, **kwargs):
                    if path == fixture["lock"]:
                        lock_modes.append(mode)
                        if mode == "a+":
                            raise PermissionError("protected_regular rejects O_CREAT on the existing lock")
                    return original_open(path, mode, *args, **kwargs)

                with mock.patch.object(Path, "open", new=guarded_open):
                    self.assertEqual(m9_budget.command_refresh_source_control_recovery_gate(mock.Mock()), 0)
                self.assertEqual(lock_modes, ["r+"])

    def test_source_control_gate_lock_refresh_rejects_post_verifier_material_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.source_gate_lock_refresh_tree(Path(temporary)) as fixture:
                verified = (
                    fixture["refresh_verdict"], fixture["replacement_verdict"], fixture["bindings"]
                )

                def verify_then_mutate():
                    fixture["replacement_verdict_path"].write_text(
                        json.dumps({**fixture["replacement_verdict"], "unexpected": True}),
                        encoding="utf-8",
                    )
                    return verified

                def source_verifier():
                    gate = json.loads(fixture["active"].read_text(encoding="utf-8"))
                    current = hashlib.sha256(fixture["replacement_verdict_path"].read_bytes()).hexdigest()
                    if gate.get("audit_report_sha256") != current:
                        raise SystemExit("source-control recovery audit report hash mismatch")
                    return gate

                with mock.patch.object(
                    m9_budget, "verify_source_control_gate_lock_refresh", side_effect=verify_then_mutate,
                ), mock.patch.object(
                    m9_budget, "verify_source_control_recovery_gate_and_hashes", side_effect=source_verifier,
                ):
                    with self.assertRaisesRegex(SystemExit, "audit report hash mismatch"):
                        m9_budget.command_refresh_source_control_recovery_gate(mock.Mock())
                active = json.loads(fixture["active"].read_text(encoding="utf-8"))
                self.assertEqual(
                    active["audit_report_sha256"], fixture["bindings"]["replacement_verdict_sha256"]
                )
                self.assertNotEqual(
                    active["audit_report_sha256"],
                    hashlib.sha256(fixture["replacement_verdict_path"].read_bytes()).hexdigest(),
                )

    def test_source_control_gate_lock_refresh_verifier_reads_replacement_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            audits = root / "audits"; audits.mkdir()
            controls = root / "controls"; controls.mkdir()
            controller = controls / "controller.py"; controller.write_text("VALUE = 1\n", encoding="utf-8")
            report = audits / "report.md"; report.write_text("PASS", encoding="utf-8")
            replacement = audits / "replacement.json"
            replacement.write_text(json.dumps({
                "schema_version": "m9-source-control-recovery-audit-verdict-v1",
                "decision_id": "D-017-source-control-recovery-v1",
                "verdict": "PASS", "blocking": 0, "non_blocking": 0,
            }), encoding="utf-8")
            auth = root / "auth.md"; auth.write_text("authorized", encoding="utf-8")
            frozen = root / "frozen.json"
            frozen.write_text(json.dumps({"files": {
                controller.as_posix(): hashlib.sha256(controller.read_bytes()).hexdigest(),
            }}), encoding="utf-8")
            verdict_path = audits / "refresh.json"
            verdict_path.write_text(json.dumps({
                "schema_version": "m9-source-control-gate-lock-refresh-audit-verdict-v1",
                "decision_id": "D-017-source-control-gate-lock-refresh-v1",
                "verdict": "PASS", "blocking": 0, "non_blocking": 0,
                "scope": "RETIRE_PRE_LOCK_MODE_GATE_AND_CREATE_REPLACEMENT_ONLY",
                "old_gate_sha256": "a" * 64, "old_gate_bytes": 10,
                "report_path": report.as_posix(),
                "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                "replacement_verdict_path": replacement.as_posix(),
                "replacement_verdict_sha256": hashlib.sha256(replacement.read_bytes()).hexdigest(),
                "frozen_hashes_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
                "authorization_record_sha256": hashlib.sha256(auth.read_bytes()).hexdigest(),
            }), encoding="utf-8")
            original_read_bytes = Path.read_bytes
            replacement_reads = 0

            def counted_read_bytes(path: Path) -> bytes:
                nonlocal replacement_reads
                if path == replacement:
                    replacement_reads += 1
                return original_read_bytes(path)

            with mock.patch.multiple(
                m9_budget,
                AUDITS=audits,
                OVERLAP_CONTROL_DIRECTORY=controls,
                SOURCE_CONTROL_GATE_LOCK_REFRESH_VERDICT=verdict_path,
                SOURCE_CONTROL_RECOVERY_LOCK_REPLACEMENT_VERDICT=replacement,
                SOURCE_CONTROL_RECOVERY_FROZEN_HASHES=frozen,
                SOURCE_CONTROL_RECOVERY_AUTHORIZATION=auth,
                SOURCE_RECOVERY_CONTROL_FILES={controller},
                PRE_LOCK_REFRESH_GATE_SHA256="a" * 64,
                PRE_LOCK_REFRESH_GATE_BYTES=10,
            ), mock.patch.object(Path, "read_bytes", new=counted_read_bytes):
                _, _, bindings = m9_budget.verify_source_control_gate_lock_refresh()
            self.assertEqual(replacement_reads, 1)
            self.assertEqual(
                bindings["replacement_verdict_sha256"],
                hashlib.sha256(replacement.read_bytes()).hexdigest(),
            )

    def test_source_control_gate_lock_refresh_rejects_link_injection_during_source_verifier(self) -> None:
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                with self.source_gate_lock_refresh_tree(root) as fixture:
                    sibling = root / f"replacement-{kind}-sibling.json"

                    def source_verifier():
                        payload = json.loads(fixture["active"].read_text(encoding="utf-8"))
                        if kind == "symlink":
                            os.replace(fixture["active"], sibling)
                            fixture["active"].symlink_to(sibling)
                        else:
                            os.link(fixture["active"], sibling)
                        return payload

                    with mock.patch.object(
                        m9_budget, "verify_source_control_recovery_gate_and_hashes",
                        side_effect=source_verifier,
                    ):
                        with self.assertRaisesRegex(
                            SystemExit,
                            "root-private control object is missing or not regular|root-private control object metadata mismatch|path drift",
                        ):
                            m9_budget.command_refresh_source_control_recovery_gate(mock.Mock())
                    journal = json.loads(fixture["refresh_journal"].read_text(encoding="utf-8"))
                    self.assertNotEqual(journal["state"], "SUCCESS_COMMITTED")

    def test_source_control_gate_lock_refresh_rechecks_replacement_at_terminal_boundaries(self) -> None:
        for phase in ("replacement_created", "success"):
            for kind in ("symlink", "hardlink"):
                with self.subTest(phase=phase, kind=kind), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    with self.source_gate_lock_refresh_tree(root) as fixture:
                        real_json = m9_budget.atomic_root_private_json
                        injected = False

                        def write_and_inject(path: Path, value: dict) -> None:
                            nonlocal injected
                            real_json(path, value)
                            expected = "REPLACEMENT_CREATED" if phase == "replacement_created" else "SUCCESS_COMMITTED"
                            if path == fixture["refresh_journal"] and value.get("state") == expected and not injected:
                                injected = True
                                sibling = root / f"terminal-{phase}-{kind}.json"
                                if kind == "symlink":
                                    os.replace(fixture["active"], sibling)
                                    fixture["active"].symlink_to(sibling)
                                else:
                                    os.link(fixture["active"], sibling)

                        with mock.patch.object(
                            m9_budget, "atomic_root_private_json", side_effect=write_and_inject,
                        ):
                            with self.assertRaisesRegex(
                                SystemExit,
                                "root-private control object is missing or not regular|root-private control object metadata mismatch|changed before terminal commit|changed during terminal commit",
                            ):
                                m9_budget.command_refresh_source_control_recovery_gate(mock.Mock())
                        self.assertTrue(injected)
                        journal = json.loads(fixture["refresh_journal"].read_text(encoding="utf-8"))
                        if phase == "replacement_created":
                            self.assertEqual(journal["state"], "REPLACEMENT_CREATED")
                        else:
                            self.assertEqual(journal["state"], "FAILED_COMMITTED")

    def test_source_control_artifact_retirement_requires_exact_receipt(self) -> None:
        self.assertEqual(m9_budget.SOURCE_CONTROL_TEST_ARTIFACT.name, "overlap_source_control_recovery.json")
        self.assertTrue(m9_budget.SOURCE_CONTROL_TEST_ARTIFACT_RETIRED.name.endswith(".test-artifact.retired.json"))

    def test_source_control_artifact_retirement_resumes_after_rename(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            retired = root / "artifact.test-artifact.retired.json"
            receipt_path = root / "receipt.json"
            journal_path = root / "journal.json"
            lock_path = root / "lock"
            gate_path = root / "gate.json"
            retired.write_text("placeholder", encoding="utf-8")
            stat = {"path": retired.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": stat["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            gate_path.write_bytes(b"gate")
            journal_path.write_text(json.dumps({"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "RENAMED", "original_path": str(root / "missing.json"), "retired_path": retired.as_posix(), "context": context, "python_bootstrap": {"python_executable": "/frozen/python"}, "original_receipt": dict(stat, path=str(root / "missing.json")), "retired_receipt": stat}), encoding="utf-8")
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=Path(temporary) / "missing.json", SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, LOCK_PATH=lock_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path), mock.patch.object(m9_budget, "file_stat_receipt", return_value=stat), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value={"python_executable": "/frozen/python"}), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                result = m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(receipt_path.read_text(encoding="utf-8"))["status"], "PASS")

    def test_cleanup_expected_runtime_hashes_are_fixed_values(self) -> None:
        values = m9_budget.cleanup_expected_runtime_hashes()
        self.assertEqual(len(values), 5)
        self.assertTrue(all(len(value) == 64 and set(value) <= set("0123456789abcdef") for value in values.values()))

    def test_cleanup_parent_security_contract_hardens_cross_uid_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            migration = parent / "migration.json"
            gate_path = parent / "gate.json"
            active = parent / "active.json"; retired = parent / "retired.json"
            gate = cleanup_security_gate(parent, migration, gate_path)
            pre = mock.Mock(st_uid=1000, st_gid=1000, st_mode=0o40755)
            owner = mock.Mock(st_uid=0, st_gid=1000, st_mode=0o40755)
            post = mock.Mock(st_uid=0, st_gid=1000, st_mode=0o41770)
            def write(path, value): path.write_text(json.dumps(value), encoding="utf-8")
            with mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json"), mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}), mock.patch.object(m9_budget, "assert_cleanup_gate_matches_verified_inode"), mock.patch.object(m9_budget.os, "lstat", side_effect=[pre, pre, owner, post]), mock.patch.object(m9_budget.os, "chown") as chown, mock.patch.object(m9_budget.os, "chmod") as chmod, mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=write), mock.patch.object(m9_budget, "cleanup_assert_single_link"), mock.patch.object(m9_budget, "cleanup_receipt_file_metadata", return_value={"uid": 0, "gid": 0, "mode": 0o600}):
                result = m9_budget.prepare_cleanup_parent_security(gate)
            self.assertEqual(result, {"path": parent.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770})
            chown.assert_called_once_with(parent, 0, 1000)
            chmod.assert_called_once_with(parent, 0o1770)
            self.assertEqual(json.loads(migration.read_text(encoding="utf-8"))["state"], "PARENT_HARDENED")

    def test_cleanup_parent_security_restores_runtime_writable_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            gate = {"cleanup_parent_security": {"before": {"path": parent.as_posix(), "uid": 1000, "gid": 1000, "mode": 0o755}, "hardened": {"path": parent.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770}, "after": {"path": parent.as_posix(), "uid": 0, "gid": 1000, "mode": 0o1770}}}
            hardened = mock.Mock(st_uid=0, st_gid=1000, st_mode=0o41770)
            with mock.patch.object(m9_budget, "MANIFESTS", parent), mock.patch.object(m9_budget.os, "lstat", return_value=hardened), mock.patch.object(m9_budget.os, "chown") as chown, mock.patch.object(m9_budget.os, "chmod") as chmod:
                m9_budget.restore_cleanup_parent_security(gate, True)
            chown.assert_not_called()
            chmod.assert_not_called()

    def test_cleanup_parent_security_resumes_after_owner_journal_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary); migration = parent / "migration.json"
            gate_path = parent / "gate.json"
            active = parent / "active.json"; retired = parent / "retired.json"
            gate = cleanup_security_gate(parent, migration, gate_path)
            state = {"uid": 1000, "gid": 1000, "mode": 0o755}; writes = 0
            def lstat(_): return mock.Mock(st_uid=state["uid"], st_gid=state["gid"], st_mode=0o40000 | state["mode"])
            def chown(_, uid, gid): state.update(uid=uid, gid=gid)
            def chmod(_, mode): state["mode"] = mode
            def write(path, value):
                nonlocal writes
                writes += 1
                if writes == 2:
                    raise OSError("injected journal failure")
                path.write_text(json.dumps(value), encoding="utf-8")
            patches = mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json")
            with patches, mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}), mock.patch.object(m9_budget, "assert_cleanup_gate_matches_verified_inode"), mock.patch.object(m9_budget.os, "lstat", side_effect=lstat), mock.patch.object(m9_budget.os, "chown", side_effect=chown), mock.patch.object(m9_budget.os, "chmod", side_effect=chmod), mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=write), mock.patch.object(m9_budget, "cleanup_assert_single_link"), mock.patch.object(m9_budget, "cleanup_receipt_file_metadata", return_value={"uid": 0, "gid": 0, "mode": 0o600}):
                with self.assertRaisesRegex(OSError, "injected journal failure"):
                    m9_budget.prepare_cleanup_parent_security(gate)
                self.assertEqual(state, {"uid": 0, "gid": 1000, "mode": 0o755})
                result = m9_budget.prepare_cleanup_parent_security(gate)
            self.assertEqual(result["mode"], 0o1770)
            self.assertEqual(json.loads(migration.read_text(encoding="utf-8"))["state"], "PARENT_HARDENED")

    def test_cleanup_artifact_security_resumes_after_chmod_journal_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary); migration = parent / "migration.json"
            gate_path = parent / "gate.json"
            active = parent / "active.json"; retired = parent / "retired.json"
            active.write_text("artifact", encoding="utf-8")
            gate = cleanup_security_gate(parent, migration, gate_path)
            binding = None
            with mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json"), mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}):
                binding = m9_budget.cleanup_security_migration_binding(gate)
            migration.write_text(json.dumps(dict(binding, state="PARENT_HARDENED")), encoding="utf-8")
            state = {"uid": 1000, "gid": 1000, "mode": 0o644}; writes = 0
            def lstat(path):
                if Path(path) == active:
                    return mock.Mock(st_uid=state["uid"], st_gid=state["gid"], st_mode=0o100000 | state["mode"], st_nlink=1)
                return mock.Mock(st_uid=0, st_gid=0, st_mode=0o100600, st_nlink=1)
            def chown(_, uid, gid): state.update(uid=uid, gid=gid)
            def chmod(_, mode): state["mode"] = mode
            def write(path, value):
                nonlocal writes
                writes += 1
                if writes == 2:
                    raise OSError("injected artifact journal failure")
                path.write_text(json.dumps(value), encoding="utf-8")
            patches = mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json")
            with patches, mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}), mock.patch.object(m9_budget.os, "lstat", side_effect=lstat), mock.patch.object(m9_budget.os, "chown", side_effect=chown), mock.patch.object(m9_budget.os, "chmod", side_effect=chmod), mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=write), mock.patch.object(m9_budget, "cleanup_assert_single_link"), mock.patch.object(m9_budget, "cleanup_receipt_file_metadata", return_value={"uid": 0, "gid": 0, "mode": 0o600}):
                with self.assertRaisesRegex(OSError, "injected artifact journal failure"):
                    m9_budget.harden_cleanup_artifact(active, True, gate)
                self.assertEqual(state, {"uid": 0, "gid": 0, "mode": 0o600})
                m9_budget.harden_cleanup_artifact(active, True, gate)
            self.assertEqual(json.loads(migration.read_text(encoding="utf-8"))["state"], "ARTIFACT_HARDENED")

    def test_cleanup_parent_security_operation_failure_matrix_is_resumable(self) -> None:
        for failure_point in ("chown", "chmod", "journal_after_chmod"):
            with self.subTest(failure_point=failure_point), tempfile.TemporaryDirectory() as temporary:
                parent = Path(temporary); migration = parent / "migration.json"
                gate_path = parent / "gate.json"
                active = parent / "active.json"; retired = parent / "retired.json"
                gate = cleanup_security_gate(parent, migration, gate_path)
                state = {"uid": 1000, "gid": 1000, "mode": 0o755}; injected = False
                def lstat(_): return mock.Mock(st_uid=state["uid"], st_gid=state["gid"], st_mode=0o40000 | state["mode"])
                def chown(_, uid, gid):
                    nonlocal injected
                    if failure_point == "chown" and not injected:
                        injected = True
                        raise OSError("injected chown failure")
                    state.update(uid=uid, gid=gid)
                def chmod(_, mode):
                    nonlocal injected
                    if failure_point == "chmod" and not injected:
                        injected = True
                        raise OSError("injected chmod failure")
                    state["mode"] = mode
                def write(path, value):
                    nonlocal injected
                    if failure_point == "journal_after_chmod" and value.get("state") == "PARENT_HARDENED" and not injected:
                        injected = True
                        raise OSError("injected final journal failure")
                    path.write_text(json.dumps(value), encoding="utf-8")
                patches = mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json")
                with patches, mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}), mock.patch.object(m9_budget, "assert_cleanup_gate_matches_verified_inode"), mock.patch.object(m9_budget.os, "lstat", side_effect=lstat), mock.patch.object(m9_budget.os, "chown", side_effect=chown), mock.patch.object(m9_budget.os, "chmod", side_effect=chmod), mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=write), mock.patch.object(m9_budget, "cleanup_assert_single_link"), mock.patch.object(m9_budget, "cleanup_receipt_file_metadata", return_value={"uid": 0, "gid": 0, "mode": 0o600}):
                    with self.assertRaisesRegex(OSError, "injected"):
                        m9_budget.prepare_cleanup_parent_security(gate)
                    result = m9_budget.prepare_cleanup_parent_security(gate)
                self.assertEqual(result, gate["cleanup_parent_security"]["hardened"])
                self.assertEqual(json.loads(migration.read_text(encoding="utf-8"))["state"], "PARENT_HARDENED")

    def test_cleanup_artifact_security_operation_failure_matrix_is_resumable(self) -> None:
        for failure_point in ("chown", "chmod", "journal_after_chmod"):
            with self.subTest(failure_point=failure_point), tempfile.TemporaryDirectory() as temporary:
                parent = Path(temporary); migration = parent / "migration.json"
                gate_path = parent / "gate.json"
                active = parent / "active.json"; retired = parent / "retired.json"
                active.write_text("artifact", encoding="utf-8")
                gate = cleanup_security_gate(parent, migration, gate_path)
                with mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json"), mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}):
                    binding = m9_budget.cleanup_security_migration_binding(gate)
                migration.write_text(json.dumps(dict(binding, state="PARENT_HARDENED")), encoding="utf-8")
                state = {"uid": 1000, "gid": 1000, "mode": 0o644}; injected = False
                def lstat(path):
                    if Path(path) == active:
                        return mock.Mock(st_uid=state["uid"], st_gid=state["gid"], st_mode=0o100000 | state["mode"], st_nlink=1)
                    return mock.Mock(st_uid=0, st_gid=0, st_mode=0o100600, st_nlink=1)
                def chown(_, uid, gid):
                    nonlocal injected
                    if failure_point == "chown" and not injected:
                        injected = True
                        raise OSError("injected chown failure")
                    state.update(uid=uid, gid=gid)
                def chmod(_, mode):
                    nonlocal injected
                    if failure_point == "chmod" and not injected:
                        injected = True
                        raise OSError("injected chmod failure")
                    state["mode"] = mode
                def write(path, value):
                    nonlocal injected
                    if failure_point == "journal_after_chmod" and value.get("state") == "ARTIFACT_HARDENED" and not injected:
                        injected = True
                        raise OSError("injected final journal failure")
                    path.write_text(json.dumps(value), encoding="utf-8")
                patches = mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json")
                with patches, mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}), mock.patch.object(m9_budget.os, "lstat", side_effect=lstat), mock.patch.object(m9_budget.os, "chown", side_effect=chown), mock.patch.object(m9_budget.os, "chmod", side_effect=chmod), mock.patch.object(m9_budget, "atomic_root_private_json", side_effect=write), mock.patch.object(m9_budget, "cleanup_assert_single_link"), mock.patch.object(m9_budget, "cleanup_receipt_file_metadata", return_value={"uid": 0, "gid": 0, "mode": 0o600}):
                    with self.assertRaisesRegex(OSError, "injected"):
                        m9_budget.harden_cleanup_artifact(active, True, gate)
                    m9_budget.harden_cleanup_artifact(active, True, gate)
                self.assertEqual(state, {"uid": 0, "gid": 0, "mode": 0o600})
                self.assertEqual(json.loads(migration.read_text(encoding="utf-8"))["state"], "ARTIFACT_HARDENED")

    def test_cleanup_security_migration_corruption_is_zero_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary); migration = parent / "migration.json"
            gate_path = parent / "gate.json"
            active = parent / "active.json"; retired = parent / "retired.json"
            gate = cleanup_security_gate(parent, migration, gate_path)
            migration.write_text(json.dumps({"schema_version": "m9-source-control-test-security-migration-v1", "state": "FORGED"}), encoding="utf-8")
            before = migration.read_bytes()
            with mock.patch.multiple(m9_budget, MANIFESTS=parent, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_SECURITY_MIGRATION=migration, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=parent, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=parent / "cleanup_gate.verified.json"), mock.patch.object(m9_budget, "stage_cleanup_gate_snapshot", return_value={"path": "snapshot", "sha256": "s" * 64, "uid": 0, "gid": 0, "mode": 0o600, "nlink": 1}), mock.patch.object(m9_budget, "cleanup_assert_single_link"), mock.patch.object(m9_budget, "cleanup_receipt_file_metadata", return_value={"uid": 0, "gid": 0, "mode": 0o600}), mock.patch.object(m9_budget.os, "chown") as chown, mock.patch.object(m9_budget.os, "chmod") as chmod:
                with self.assertRaisesRegex(SystemExit, "journal binding mismatch"):
                    m9_budget.prepare_cleanup_parent_security(gate)
            self.assertEqual(migration.read_bytes(), before)
            chown.assert_not_called()
            self.assertNotIn(mock.call(parent, 0o1770), chmod.mock_calls)

    def test_cleanup_verified_gate_replacement_matrix_is_zero_write(self) -> None:
        for replacement_kind in ("not_json", "incomplete_pass", "complete_alternate_pass", "deleted"):
            with self.subTest(replacement_kind=replacement_kind), tempfile.TemporaryDirectory() as temporary:
                parent = Path(temporary); trust = parent / "trusted"; migration = trust / "migration.json"
                gate_path = parent / "gate.json"; gate = cleanup_security_gate(parent, migration, gate_path)
                if replacement_kind == "deleted":
                    gate_path.unlink()
                elif replacement_kind == "not_json":
                    gate_path.write_bytes(b"NOT-JSON")
                elif replacement_kind == "incomplete_pass":
                    gate_path.write_bytes(b'{"status":"PASS"}\n')
                else:
                    alternate = json.loads(gate["_verified_gate_bytes"].decode("utf-8"))
                    alternate["audit_report_sha256"] = "z" * 64
                    gate_path.write_bytes((json.dumps(alternate, sort_keys=True) + "\n").encode("utf-8"))
                with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=trust, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=trust / "cleanup_gate.verified.json"), mock.patch.object(m9_budget, "atomic_root_private_bytes") as writer:
                    with self.assertRaisesRegex(SystemExit, "gate path"):
                        m9_budget.stage_cleanup_gate_snapshot(gate)
                self.assertFalse(trust.exists())
                writer.assert_not_called()

    def test_cleanup_gate_replacement_during_snapshot_is_rejected_before_parent_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary); trust = parent / "trusted"; migration = trust / "migration.json"
            gate_path = parent / "gate.json"; snapshot = trust / "cleanup_gate.verified.json"
            gate = cleanup_security_gate(parent, migration, gate_path)
            real_lstat = os.lstat
            def lstat(path):
                value = real_lstat(path)
                if Path(path) == trust:
                    return mock.Mock(st_mode=value.st_mode, st_uid=0, st_gid=0)
                return value
            def replace_gate(path, payload):
                path.write_bytes(payload)
                os.chmod(path, 0o600)
                gate_path.write_bytes(b"REPLACED-AFTER-VERIFICATION")
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, SOURCE_CONTROL_TEST_TRUST_ROOT=trust, SOURCE_CONTROL_TEST_GATE_SNAPSHOT=snapshot), mock.patch.object(m9_budget.os, "lstat", side_effect=lstat), mock.patch.object(m9_budget, "atomic_root_private_bytes", side_effect=replace_gate), mock.patch.object(m9_budget.os, "chown") as chown, mock.patch.object(m9_budget.os, "chmod") as chmod:
                with self.assertRaisesRegex(SystemExit, "gate path drift"):
                    m9_budget.stage_cleanup_gate_snapshot(gate)
            chown.assert_not_called()
            self.assertNotIn(mock.call(parent, 0o1770), chmod.mock_calls)

    def test_atomic_private_durable_bytes_failure_matrix_is_resumable(self) -> None:
        for failure_point in ("file_fsync", "replace", "target_recheck", "target_fsync", "directory_fsync"):
            with self.subTest(failure_point=failure_point), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "journal.json"; payload = b'{"state":"PREPARED"}\n'
                real_fsync = os.fsync; real_replace = os.replace; real_lstat = os.lstat; fsync_calls = 0; injected = False
                def fsync(fd):
                    nonlocal fsync_calls, injected
                    fsync_calls += 1
                    target = {"file_fsync": 1, "target_fsync": 2, "directory_fsync": 3}.get(failure_point)
                    if target is not None and fsync_calls == target and not injected:
                        injected = True
                        raise OSError("injected fsync failure")
                    return real_fsync(fd)
                def replace(src, dst):
                    nonlocal injected
                    if failure_point == "replace" and not injected:
                        injected = True
                        raise OSError("injected replace failure")
                    return real_replace(src, dst)
                def lstat(target):
                    nonlocal injected
                    if failure_point == "target_recheck" and Path(target) == path and path.exists() and not injected:
                        injected = True
                        raise OSError("injected target recheck failure")
                    return real_lstat(target)
                with mock.patch.object(m9_budget.os, "fsync", side_effect=fsync), mock.patch.object(m9_budget.os, "replace", side_effect=replace), mock.patch.object(m9_budget.os, "lstat", side_effect=lstat):
                    with self.assertRaisesRegex(OSError, "injected"):
                        m9_budget.atomic_private_durable_bytes(path, payload, os.getuid(), os.getgid())
                tmp = path.with_suffix(".json.tmp")
                if failure_point in ("file_fsync", "replace"):
                    self.assertFalse(path.exists()); self.assertTrue(tmp.exists())
                else:
                    self.assertEqual(path.read_bytes(), payload); self.assertFalse(tmp.exists())
                m9_budget.atomic_private_durable_bytes(path, payload, os.getuid(), os.getgid())
                self.assertEqual(path.read_bytes(), payload)
                self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_atomic_private_durable_bytes_rejects_hostile_temporary_paths(self) -> None:
        for kind in ("symlink", "hardlink", "wrong_mode"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary); path = root / "journal.json"; tmp = root / "journal.json.tmp"; sibling = root / "sibling"
                if kind == "symlink":
                    sibling.write_bytes(b"target"); tmp.symlink_to(sibling)
                elif kind == "hardlink":
                    sibling.write_bytes(b"target"); os.chmod(sibling, 0o600); os.link(sibling, tmp)
                else:
                    tmp.write_bytes(b"target"); os.chmod(tmp, 0o644)
                with self.assertRaisesRegex(SystemExit, "temporary file mismatch"):
                    m9_budget.atomic_private_durable_bytes(path, b"payload", os.getuid(), os.getgid())
                self.assertFalse(path.exists())

    def test_atomic_private_durable_bytes_overwrites_owned_partial_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "journal.json"; tmp = path.with_suffix(".json.tmp")
            tmp.write_bytes(b"partial"); os.chmod(tmp, 0o600)
            payload = b'{"state":"PARENT_OWNER"}\n'
            m9_budget.atomic_private_durable_bytes(path, payload, os.getuid(), os.getgid())
            self.assertEqual(path.read_bytes(), payload)
            self.assertFalse(tmp.exists())

    def test_atomic_private_durable_bytes_rejects_wrong_owner_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "journal.json"; tmp = path.with_suffix(".json.tmp")
            tmp.write_bytes(b"partial"); os.chmod(tmp, 0o600)
            actual = os.lstat(tmp)
            wrong_owner = mock.Mock(st_mode=actual.st_mode, st_nlink=1, st_uid=os.getuid() + 1, st_gid=os.getgid())
            with mock.patch.object(m9_budget.os, "fstat", return_value=wrong_owner):
                with self.assertRaisesRegex(SystemExit, "temporary file mismatch"):
                    m9_budget.atomic_private_durable_bytes(path, b"payload", os.getuid(), os.getgid())
            self.assertFalse(path.exists())
            self.assertEqual(tmp.read_bytes(), b"partial")

    def test_cleanup_journal_schema_and_paths_are_fixed(self) -> None:
        self.assertEqual(m9_budget.SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL.name, "overlap_source_control_test_artifact_cleanup.json")

    def test_cleanup_prepared_active_drift_is_zero_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; retired = root / "retired.json"; journal = root / "journal.json"
            active.write_text("DRIFTED", encoding="utf-8")
            original = {"path": active.as_posix(), "bytes": 3, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            journal.write_text(json.dumps({"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "PREPARED", "original_path": active.as_posix(), "retired_path": retired.as_posix(), "original_receipt": original, "context": {}}), encoding="utf-8")
            with mock.patch.object(m9_budget, "file_stat_receipt", return_value={"path": active.as_posix(), "bytes": 7, "sha256": "d" * 64, "uid": 1000, "gid": 1000, "mode": 0o644}):
                self.assertNotEqual(original, m9_budget.file_stat_receipt(active))
            self.assertTrue(active.exists())
            self.assertFalse(retired.exists())

    def test_cleanup_prepared_active_drift_rejects_through_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; retired = root / "retired.json"
            receipt_path = root / "receipt.json"; journal_path = root / "journal.json"
            lock_path = root / "lock"; gate_path = root / "gate.json"
            active.write_text("DRIFTED", encoding="utf-8")
            gate_path.write_bytes(b"gate")
            original = {"path": active.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": original["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            bootstrap = {"python_executable": "/frozen/python"}
            journal_payload = {"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "PREPARED", "original_path": active.as_posix(), "retired_path": retired.as_posix(), "original_receipt": original, "context": context, "python_bootstrap": bootstrap}
            journal_path.write_text(json.dumps(journal_payload), encoding="utf-8")
            before = {p: p.read_bytes() for p in (active, journal_path)}

            def stat(path):
                path = Path(path)
                if path == active:
                    return dict(original, path=active.as_posix(), bytes=7, sha256="d" * 64)
                return dict(original, path=path.as_posix())

            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "file_stat_receipt", side_effect=stat), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value=bootstrap), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                with self.assertRaisesRegex(SystemExit, "cleanup PREPARED original receipt drift"):
                    m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            self.assertEqual(active.read_bytes(), before[active])
            self.assertEqual(journal_path.read_bytes(), before[journal_path])
            self.assertFalse(retired.exists())
            self.assertFalse(receipt_path.exists())

    def test_cleanup_renamed_existing_receipt_is_preserved_through_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; retired = root / "retired.json"; receipt_path = root / "receipt.json"
            journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            retired.write_text("cap", encoding="utf-8"); gate_path.write_bytes(b"gate")
            original = {"path": active.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            retired_receipt = dict(original, path=retired.as_posix())
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": original["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            bootstrap = {"python_executable": "/frozen/python"}
            journal_payload = {"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "RENAMED", "original_path": active.as_posix(), "retired_path": retired.as_posix(), "original_receipt": original, "retired_receipt": retired_receipt, "context": context, "python_bootstrap": bootstrap}
            journal_path.write_text(json.dumps(journal_payload), encoding="utf-8")
            receipt_payload = {"schema_version": "m9-source-control-test-artifact-retirement-v1", "status": "PASS", "original": original, "retired": retired_receipt, "context": context, "reason": "test_isolation_failure_artifact", "utc": "2026-01-01T00:00:00Z", "python_bootstrap": bootstrap}
            receipt_path.write_text(json.dumps(receipt_payload), encoding="utf-8")
            receipt_before = receipt_path.read_bytes()

            def stat(path):
                return dict(original, path=Path(path).as_posix())

            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "file_stat_receipt", side_effect=stat), mock.patch.object(m9_budget, "cleanup_receipt_file_metadata", return_value={"uid": 1000, "gid": 1000, "mode": 0o600}), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value=bootstrap), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                self.assertEqual(m9_budget.command_retire_source_control_test_artifact(mock.Mock()), 0)
            self.assertEqual(receipt_path.read_bytes(), receipt_before)
            self.assertEqual(json.loads(journal_path.read_text(encoding="utf-8"))["state"], "SUCCESS_COMMITTED")

    def test_cleanup_success_forged_receipt_rejects_through_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; retired = root / "retired.json"; receipt_path = root / "receipt.json"
            journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            retired.write_text("cap", encoding="utf-8"); gate_path.write_bytes(b"gate")
            original = {"path": active.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            retired_receipt = dict(original, path=retired.as_posix())
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": original["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            bootstrap = {"python_executable": "/frozen/python"}
            journal_payload = {"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "SUCCESS_COMMITTED", "original_path": active.as_posix(), "retired_path": retired.as_posix(), "original_receipt": original, "retired_receipt": retired_receipt, "context": context, "python_bootstrap": bootstrap}
            journal_path.write_text(json.dumps(journal_payload), encoding="utf-8")
            receipt_path.write_text(json.dumps({"status": "FORGED", "context": context}), encoding="utf-8")
            before = {p: p.read_bytes() for p in (journal_path, receipt_path, retired)}

            def stat(path):
                return dict(original, path=Path(path).as_posix())

            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "file_stat_receipt", side_effect=stat), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value=bootstrap), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                with self.assertRaisesRegex(SystemExit, "cleanup receipt content mismatch"):
                    m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            for path, payload in before.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_cleanup_prepared_after_rename_window_resumes_through_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; retired = root / "retired.json"; receipt_path = root / "receipt.json"; journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            retired.write_text("cap", encoding="utf-8"); gate_path.write_bytes(b"gate")
            original = {"path": active.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": original["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            journal_path.write_text(json.dumps({"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "PREPARED", "original_path": active.as_posix(), "retired_path": retired.as_posix(), "original_receipt": original, "context": context, "python_bootstrap": {"python_executable": "/frozen/python"}}), encoding="utf-8")
            def stat(path):
                p = Path(path)
                return dict(original, path=p.as_posix())
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "file_stat_receipt", side_effect=stat), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value={"python_executable": "/frozen/python"}), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                self.assertEqual(m9_budget.command_retire_source_control_test_artifact(mock.Mock()), 0)
            self.assertFalse(active.exists())
            self.assertTrue(retired.exists())
            self.assertEqual(json.loads(journal_path.read_text(encoding="utf-8"))["state"], "SUCCESS_COMMITTED")

    def test_cleanup_prepared_existing_receipt_rejects_before_rename(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; retired = root / "retired.json"; receipt_path = root / "receipt.json"
            journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            active.write_text("cap", encoding="utf-8"); gate_path.write_bytes(b"gate")
            original = {"path": active.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": original["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            bootstrap = {"python_executable": "/frozen/python"}
            journal_path.write_text(json.dumps({"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "PREPARED", "original_path": active.as_posix(), "retired_path": retired.as_posix(), "original_receipt": original, "context": context, "python_bootstrap": bootstrap}), encoding="utf-8")
            receipt_path.write_text(json.dumps({"status": "FORGED"}), encoding="utf-8")
            before = {p: p.read_bytes() for p in (active, journal_path, receipt_path)}
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value=bootstrap), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                with self.assertRaisesRegex(SystemExit, "cleanup PREPARED receipt must be absent"):
                    m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            for path, payload in before.items():
                self.assertEqual(path.read_bytes(), payload)
            self.assertFalse(retired.exists())

    def test_cleanup_symlink_artifact_rejects_before_rename(self) -> None:
        if not hasattr(Path, "symlink_to"):
            self.skipTest("symlink unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.json"; active = root / "active.json"; retired = root / "retired.json"
            receipt_path = root / "receipt.json"; journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            target.write_text("cap", encoding="utf-8"); active.symlink_to(target); gate_path.write_bytes(b"gate")
            before = active.read_bytes()
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value={"python_executable": "/frozen/python"}), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74"}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value={"runtime": "x"}), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                with self.assertRaisesRegex(SystemExit, "forbids symlink paths"):
                    m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            self.assertTrue(active.is_symlink()); self.assertEqual(active.read_bytes(), before); self.assertFalse(retired.exists())

    def test_cleanup_hardlinked_artifact_rejects_before_rename(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; sibling = root / "sibling.json"; retired = root / "retired.json"
            receipt_path = root / "receipt.json"; journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            active.write_text("cap", encoding="utf-8"); os.link(active, sibling); gate_path.write_bytes(b"gate")
            before = active.read_bytes()
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value={"python_executable": "/frozen/python"}), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74"}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value={"runtime": "x"}), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                with self.assertRaisesRegex(SystemExit, "requires single-link paths"):
                    m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            self.assertTrue(active.exists()); self.assertEqual(active.read_bytes(), before); self.assertTrue(sibling.exists()); self.assertFalse(retired.exists())

    def test_cleanup_post_rename_hardlink_injection_rejects_before_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "active.json"; sibling = root / "sibling.json"; retired = root / "retired.json"
            receipt_path = root / "receipt.json"; journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            active.write_text("cap", encoding="utf-8"); gate_path.write_bytes(b"gate")
            original = {"path": active.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": original["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            bootstrap = {"python_executable": "/frozen/python"}
            real_replace = os.replace
            def replace_and_inject(src, dst):
                real_replace(src, dst)
                if Path(src) == active and Path(dst) == retired:
                    os.link(retired, sibling)
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "file_stat_receipt", return_value=original), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value=bootstrap), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0), mock.patch.object(m9_budget.os, "replace", side_effect=replace_and_inject):
                with self.assertRaisesRegex(SystemExit, "requires single-link paths"):
                    m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            self.assertFalse(active.exists()); self.assertTrue(retired.exists()); self.assertTrue(sibling.exists()); self.assertFalse(receipt_path.exists())

    def test_cleanup_renamed_receipt_drift_rejects_through_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); active = root / "active.json"; retired = root / "retired.json"; receipt_path = root / "receipt.json"; journal_path = root / "journal.json"; lock_path = root / "lock"; gate_path = root / "gate.json"
            retired.write_text("cap", encoding="utf-8"); gate_path.write_bytes(b"gate")
            original = {"path": active.as_posix(), "bytes": 1644, "sha256": "2e0aa63648b7ab890eebb140b9b1bd4d416dd22085aab0351f3e39bb1ec9fc74", "uid": 1000, "gid": 1000, "mode": 0o644, "nlink": 1}
            context = {"gate_sha256": hashlib.sha256(b"gate").hexdigest(), "frozen_sha256": "f" * 64, "authorization_sha256": "a" * 64, "audit_report_sha256": "r" * 64, "artifact_sha256": original["sha256"], "fixed_runtime_sha256": {"runtime": "x"}}
            good_retired = dict(original, path=retired.as_posix())
            journal_path.write_text(json.dumps({"schema_version": "m9-source-control-test-artifact-cleanup-v1", "state": "RENAMED", "original_path": active.as_posix(), "retired_path": retired.as_posix(), "original_receipt": original, "retired_receipt": good_retired, "context": context, "python_bootstrap": {"python_executable": "/frozen/python"}}), encoding="utf-8")
            receipt_path.write_text(json.dumps({"status": "PASS", "context": context, "original": original, "retired": dict(good_retired, sha256="0" * 64)}), encoding="utf-8")
            def stat(path): return dict(original, path=Path(path).as_posix())
            with mock.patch.multiple(m9_budget, SOURCE_CONTROL_TEST_ARTIFACT=active, SOURCE_CONTROL_TEST_ARTIFACT_RETIRED=retired, SOURCE_CONTROL_TEST_ARTIFACT_RECEIPT=receipt_path, SOURCE_CONTROL_TEST_ARTIFACT_JOURNAL=journal_path, SOURCE_CONTROL_TEST_CLEANUP_GATE=gate_path, LOCK_PATH=lock_path, SOURCE_CONTROL_RECOVERY_GATE=root / "no-gate", SOURCE_CONTROL_RECOVERY_PARENT=root / "no-parent"), mock.patch.object(m9_budget, "file_stat_receipt", side_effect=stat), mock.patch.object(m9_budget, "isolated_bootstrap_provenance", return_value={"python_executable": "/frozen/python"}), mock.patch.object(m9_budget, "verify_source_control_test_cleanup_gate", return_value={"frozen_sha256": context["frozen_sha256"], "authorization_sha256": context["authorization_sha256"], "audit_report_sha256": context["audit_report_sha256"], "artifact_sha256": context["artifact_sha256"]}), mock.patch.object(m9_budget, "cleanup_runtime_receipt", return_value=context["fixed_runtime_sha256"]), mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                with self.assertRaisesRegex(SystemExit, "cleanup receipt content mismatch"):
                    m9_budget.command_retire_source_control_test_artifact(mock.Mock())
            self.assertTrue(retired.exists()); self.assertTrue(receipt_path.exists())


class UnlimitedWallClockMigrationTests(unittest.TestCase):
    def policy(self) -> dict[str, object]:
        return {
            "mode": "UNLIMITED",
            "decision_id": "D-018",
            "historical_limit_seconds": m9_budget.HISTORICAL_WALL_LIMIT,
            "historical_start_utc": m9_budget.FROZEN_START,
            "historical_deadline_utc": m9_budget.FROZEN_DEADLINE,
            "migration_transaction_id": "d018-unlimited-wall-clock-20260820-01",
            "migration_event_id": "d018-unlimited-wall-clock-20260820-01:unlimited-wall-clock",
            "authorization_sha256": "a" * 64,
            "contract_sha256": "c" * 64,
            "gate_sha256": "1" * 64,
        }

    def limited_state(self) -> dict[str, object]:
        return {
            "schema_version": "m9-budget-state-v1",
            "start_utc": m9_budget.FROZEN_START,
            "deadline_utc": m9_budget.FROZEN_DEADLINE,
            "vhdx_baseline_bytes": 0,
            "gpu_seconds": {key: 0.0 for key in m9_budget.GPU_LIMITS},
            "cpu_seconds": {key: 0.0 for key in m9_budget.CPU_LIMITS},
            "cpu_adjustments": [],
            "hard_stopped": False,
            "active_overlap_transaction": None,
        }

    def test_limited_expired_and_unlimited_policy_are_distinct(self) -> None:
        limited = self.limited_state()
        self.assertEqual(m9_budget.wall_clock_policy_mode(limited), "LIMITED")
        self.assertIn("wall_clock_limit", m9_budget.violations(limited))
        unlimited = dict(limited, wall_clock_policy=self.policy())
        self.assertEqual(m9_budget.wall_clock_policy_mode(unlimited), "UNLIMITED")
        self.assertIsNone(m9_budget.deadline_remaining(unlimited))
        self.assertNotIn("wall_clock_limit", m9_budget.violations(unlimited))

    def test_malformed_unlimited_policy_is_rejected(self) -> None:
        malformed = dict(self.policy(), contract_sha256="bad")
        state = dict(self.limited_state(), wall_clock_policy=malformed)
        self.assertEqual(m9_budget.wall_clock_policy_mode(state), "INVALID")
        self.assertIn("wall_clock_policy_invalid", m9_budget.violations(state))

    def test_projection_skips_only_unlimited_wall_clock(self) -> None:
        state = {
            "completed_structure_ids": ["500"],
            "smoke_elapsed_seconds": 1.0,
            "smoke_payload_increment_bytes": 1,
        }
        status = {
            "deadline_remaining_seconds": None,
            "cpu_seconds": {"overlap_batch": 0.0},
            "storage": {
                "combined_apparent_bytes_since_overlap_baseline": 0,
                "combined_allocated_bytes_since_overlap_baseline": 0,
                "host_vhdx_growth_since_overlap_baseline_bytes": 0,
                "combined_apparent_bytes": 0,
                "combined_allocated_bytes": 0,
                "host_vhdx_growth_from_start_bytes": 0,
            },
        }
        projection = compute_projection(contract(), state, status)
        self.assertNotIn("projected_overall_wall_clock", projection["reasons"])
        status["deadline_remaining_seconds"] = 1.0
        projection = compute_projection(contract(), state, status)
        self.assertIn("projected_overall_wall_clock", projection["reasons"])

    def migration_fixture(
        self, root: Path
    ) -> tuple[contextlib.ExitStack, dict[str, Path], dict[str, object], dict[str, object], bytes]:
        paths = {
            "state": root / "budget_state.json",
            "workflow": root / "workflow.json",
            "ledger": root / "ledger.jsonl",
            "overlap_tx": root / "overlap_transaction.json",
            "source_tx": root / "source_recovery.json",
            "source_gate": root / "source_recovery_gate.json",
            "old_gate": root / "overlap_gate.json",
            "retired_gate": root / "overlap_gate.retired.json",
            "d018_gate": root / "d018_gate.json",
            "d018_tx": root / "d018_transaction.json",
            "execution_gate": root / "d018_execution_gate.json",
            "execution_verdict": root / "d018_execution_verdict.json",
            "execution_report": root / "d018_execution_report.md",
            "journal": root / "journal.json",
            "snapshot": root / "snapshot.json",
            "lock": root / "budget.lock",
        }
        state = self.limited_state()
        state.update({
            "last_event_utc": m9_budget.FROZEN_START,
            "overlap_storage_baseline": {
                "combined_apparent_bytes": 0,
                "combined_allocated_bytes": 0,
                "host_vhdx_bytes": 0,
            },
        })
        objects = {
            "state": state,
            "workflow": {
                "schema_version": "m9-overlap-workflow-state-v1",
                "stage": "AUDIT_PASSED",
                "hard_stopped": False,
                "active_transaction": None,
            },
            "overlap_tx": {"transaction_id": "parent", "state": "SUCCESS_COMMITTED"},
            "source_tx": {"transaction_id": "recovery", "state": "SUCCESS_COMMITTED"},
            "source_gate": {"schema_version": "m9-source-control-recovery-gate-v1"},
            "old_gate": {"schema_version": "m9-overlap-audit-gate-v1", "status": "PASS"},
        }
        for name, value in objects.items():
            paths[name].write_text(json.dumps(value) + "\n", encoding="utf-8")
        paths["ledger"].write_text(
            json.dumps({"event_id": "prefix", "event": "PREFIX"}) + "\n",
            encoding="utf-8",
        )
        os.chown(paths["ledger"], 1000, 1000)
        os.chmod(paths["ledger"], 0o644)
        paths["lock"].write_text("lock\n", encoding="utf-8")
        paths["d018_gate"].write_text("{}\n", encoding="utf-8")
        os.chown(paths["d018_gate"], 0, 1000)
        os.chmod(paths["d018_gate"], 0o640)
        replacement = {
            "schema_version": "m9-overlap-audit-gate-v1",
            "status": "PASS",
            "blocking": 0,
            "non_blocking": 0,
            "decision_id": "D-018",
        }
        replacement_bytes = (
            json.dumps(replacement, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        bindings = {
            "gate": {
                "path": paths["d018_gate"].as_posix(),
                "bytes": 3,
                "sha256": "1" * 64,
                "uid": 0,
                "gid": 1000,
                "mode": 0o640,
                "nlink": 1,
            },
            "authorization_sha256": "a" * 64,
            "contract_sha256": "c" * 64,
        }
        gate = {
            "migration_transaction_id": "d018-unlimited-wall-clock-20260820-01",
            "migration_event_id": "d018-unlimited-wall-clock-20260820-01:unlimited-wall-clock",
            "replacement_overlap_gate_sha256": hashlib.sha256(replacement_bytes).hexdigest(),
            "replacement_overlap_gate_bytes": len(replacement_bytes),
        }
        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch.multiple(
            m9_budget,
            STATE_PATH=paths["state"],
            OVERLAP_WORKFLOW_STATE=paths["workflow"],
            LEDGER_PATH=paths["ledger"],
            OVERLAP_TRANSACTION=paths["overlap_tx"],
            SOURCE_CONTROL_RECOVERY_TRANSACTION=paths["source_tx"],
            SOURCE_CONTROL_RECOVERY_GATE=paths["source_gate"],
            OVERLAP_AUDIT_GATE=paths["old_gate"],
            OVERLAP_AUDIT_GATE_PRE_D018_RETIRED=paths["retired_gate"],
            UNLIMITED_WALL_CLOCK_GATE=paths["d018_gate"],
            UNLIMITED_WALL_CLOCK_TRANSACTION=paths["d018_tx"],
            UNLIMITED_WALL_CLOCK_EXECUTION_GATE=paths["execution_gate"],
            UNLIMITED_WALL_CLOCK_EXECUTION_VERDICT=paths["execution_verdict"],
            UNLIMITED_WALL_CLOCK_EXECUTION_REPORT=paths["execution_report"],
            UNLIMITED_WALL_CLOCK_JOURNAL=paths["journal"],
            UNLIMITED_WALL_CLOCK_PRE_STATE_SNAPSHOT=paths["snapshot"],
            LOCK_PATH=paths["lock"],
            SOURCE_RECOVERY_PRODUCTS=tuple(),
        ))
        stack.enter_context(mock.patch.object(
            m9_budget,
            "isolated_bootstrap_provenance",
            return_value={"python_executable": "/frozen/python"},
        ))
        stack.enter_context(mock.patch.object(
            m9_budget,
            "verify_unlimited_wall_clock_gate_and_hashes",
            return_value=(gate, bindings, replacement_bytes),
        ))
        stack.enter_context(mock.patch.object(
            m9_budget, "verify_d017_history_bound_by_d018", return_value=None
        ))
        gate["pre_runtime"] = m9_budget.d018_runtime_receipts()
        return stack, paths, gate, bindings, replacement_bytes

    def test_full_migration_and_terminal_replay_are_single_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, gate, _, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 0)
                first = {path: path.read_bytes() for path in paths.values() if path.exists()}
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 0)
                second = {path: path.read_bytes() for path in paths.values() if path.exists()}
                self.assertEqual(first, second)
                self.assertEqual(json.loads(paths["journal"].read_text())["state"], "SUCCESS_COMMITTED")
                self.assertEqual(json.loads(paths["d018_tx"].read_text())["state"], "SUCCESS_COMMITTED")
                count = sum(
                    1
                    for line in paths["ledger"].read_text().splitlines()
                    if json.loads(line).get("event_id") == gate["migration_event_id"]
                )
                self.assertEqual(count, 1)
                self.assertEqual(
                    m9_budget.wall_clock_policy_mode(json.loads(paths["state"].read_text())),
                    "UNLIMITED",
                )

    def test_migration_resumes_all_persistent_commit_windows(self) -> None:
        targets = (
            "OLD_GATE_RETIRED",
            "NEW_GATE_CREATED",
            "LEDGER_COMMITTED",
            "STATE_COMMITTED",
            "SUCCESS_COMMITTED",
        )
        for target in targets:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                stack, paths, gate, _, _ = self.migration_fixture(Path(temporary))
                with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                    real_write = m9_budget.atomic_root_private_json
                    injected = False

                    def interrupt(path: Path, value: dict[str, object]) -> None:
                        nonlocal injected
                        if (
                            Path(path) == paths["journal"]
                            and value.get("state") == target
                            and not injected
                        ):
                            injected = True
                            raise m9_budget.D018SimulatedPowerLoss(f"injected:{target}")
                        real_write(path, value)

                    with mock.patch.object(
                        m9_budget, "atomic_root_private_json", side_effect=interrupt
                    ):
                        with self.assertRaisesRegex(m9_budget.D018SimulatedPowerLoss, target):
                            m9_budget.command_migrate_unlimited_wall_clock(mock.Mock())
                    self.assertEqual(
                        m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 0
                    )
                    self.assertEqual(
                        json.loads(paths["journal"].read_text())["state"],
                        "SUCCESS_COMMITTED",
                    )
                    count = sum(
                        1
                        for line in paths["ledger"].read_text().splitlines()
                        if json.loads(line).get("event_id") == gate["migration_event_id"]
                    )
                    self.assertEqual(count, 1)

    def test_prepared_journal_precedes_snapshot_and_resumes_power_loss(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, _, _, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                real_write = m9_budget.atomic_root_private_bytes
                injected = False

                def lose_power(path: Path, payload: bytes) -> None:
                    nonlocal injected
                    if Path(path) == paths["snapshot"] and not injected:
                        injected = True
                        raise m9_budget.D018SimulatedPowerLoss("before-snapshot")
                    real_write(path, payload)

                with mock.patch.object(
                    m9_budget, "atomic_root_private_bytes", side_effect=lose_power
                ):
                    with self.assertRaisesRegex(
                        m9_budget.D018SimulatedPowerLoss, "before-snapshot"
                    ):
                        m9_budget.command_migrate_unlimited_wall_clock(mock.Mock())
                self.assertTrue(paths["journal"].exists())
                self.assertFalse(paths["snapshot"].exists())
                self.assertEqual(
                    json.loads(paths["journal"].read_text())["state"], "PREPARED"
                )
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 0)

    def test_snapshot_creation_failure_commits_unique_double_hard_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, _, _, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                real_write = m9_budget.atomic_root_private_bytes

                def fail_snapshot(path: Path, payload: bytes) -> None:
                    if Path(path) == paths["snapshot"]:
                        raise OSError("snapshot-io-failure")
                    real_write(path, payload)

                with mock.patch.object(
                    m9_budget,
                    "atomic_root_private_bytes",
                    side_effect=fail_snapshot,
                ):
                    self.assertEqual(
                        m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 125
                    )
                self.assertTrue(paths["journal"].exists())
                self.assertFalse(paths["snapshot"].exists())
                self.assertTrue(json.loads(paths["state"].read_text())["hard_stopped"])
                self.assertTrue(json.loads(paths["workflow"].read_text())["hard_stopped"])
                self.assertEqual(
                    json.loads(paths["d018_tx"].read_text())["state"],
                    "FAILED_COMMITTED",
                )
                events = [
                    json.loads(line)
                    for line in paths["ledger"].read_text().splitlines()
                    if json.loads(line).get("event")
                    == "M9_UNLIMITED_WALL_CLOCK_MIGRATION_HARD_STOP"
                ]
                self.assertEqual(len(events), 1)

    def test_runtime_drift_rejects_before_first_migration_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, _, _, _ = self.migration_fixture(Path(temporary))
            paths["workflow"].write_text('{"schema_version":"m9-overlap-workflow-state-v1","stage":"DRIFT"}\n', encoding="utf-8")
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                with self.assertRaisesRegex(SystemExit, "formal runtime differs"):
                    m9_budget.command_migrate_unlimited_wall_clock(mock.Mock())
            self.assertFalse(paths["journal"].exists())
            self.assertFalse(paths["snapshot"].exists())
            self.assertFalse(paths["retired_gate"].exists())
            self.assertFalse(paths["d018_tx"].exists())

    def test_partial_ledger_append_is_rolled_back_and_resumed_exactly_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, gate, bindings, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                real_append = m9_budget.append_existing_regular_bytes
                injected = False

                def partial(path: Path, payload: bytes, **kwargs: object) -> None:
                    nonlocal injected
                    if Path(path) == paths["ledger"] and not injected:
                        injected = True
                        descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
                        try:
                            os.write(descriptor, payload[: max(1, len(payload) // 2)])
                            os.fsync(descriptor)
                        finally:
                            os.close(descriptor)
                        raise m9_budget.D018SimulatedPowerLoss("partial-ledger")
                    real_append(path, payload, **kwargs)

                with mock.patch.object(
                    m9_budget, "append_existing_regular_bytes", side_effect=partial
                ):
                    with self.assertRaisesRegex(
                        m9_budget.D018SimulatedPowerLoss, "partial-ledger"
                    ):
                        m9_budget.command_migrate_unlimited_wall_clock(mock.Mock())
                self.assertEqual(
                    json.loads(paths["journal"].read_text())["state"],
                    "NEW_GATE_CREATED",
                )
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 0)
                event = m9_budget.d018_migration_event(
                    json.loads(paths["journal"].read_text()), gate, bindings
                )
                prefix = (json.dumps({"event_id": "prefix", "event": "PREFIX"}) + "\n").encode()
                self.assertEqual(
                    paths["ledger"].read_bytes(),
                    prefix + m9_budget.canonical_ledger_event_bytes(event),
                )

    def test_same_byte_inode_swap_is_rejected_and_double_hard_stopped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, _, _, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                real_replace = os.replace
                injected = False

                def swap(source: object, destination: object) -> None:
                    nonlocal injected
                    source_path = Path(source)
                    destination_path = Path(destination)
                    if source_path == paths["old_gate"] and not injected:
                        injected = True
                        alternate = paths["old_gate"].with_suffix(".swap")
                        alternate.write_bytes(source_path.read_bytes())
                        os.chown(alternate, os.lstat(source_path).st_uid, os.lstat(source_path).st_gid)
                        os.chmod(alternate, stat.S_IMODE(os.lstat(source_path).st_mode))
                        real_replace(alternate, source_path)
                    real_replace(source_path, destination_path)

                with mock.patch.object(m9_budget.os, "replace", side_effect=swap):
                    self.assertEqual(
                        m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 125
                    )
                self.assertTrue(json.loads(paths["state"].read_text())["hard_stopped"])
                self.assertTrue(json.loads(paths["workflow"].read_text())["hard_stopped"])
                self.assertEqual(
                    json.loads(paths["d018_tx"].read_text())["state"],
                    "FAILED_COMMITTED",
                )

    def test_deterministic_terminal_failure_commits_one_failure_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, _, _, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0), mock.patch.object(
                m9_budget,
                "verify_unlimited_wall_clock_execution_ready",
                side_effect=SystemExit("terminal-drift"),
            ):
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 125)
                first = paths["ledger"].read_bytes()
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 125)
                self.assertEqual(paths["ledger"].read_bytes(), first)
                failure_ids = [
                    json.loads(line).get("event_id")
                    for line in paths["ledger"].read_text().splitlines()
                    if json.loads(line).get("event")
                    == "M9_UNLIMITED_WALL_CLOCK_MIGRATION_HARD_STOP"
                ]
                self.assertEqual(len(failure_ids), 1)
                self.assertTrue(json.loads(paths["state"].read_text())["hard_stopped"])
                self.assertTrue(json.loads(paths["workflow"].read_text())["hard_stopped"])

    def test_terminal_evidence_drift_matrix_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, _, _, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 0)
                evidence = (
                    paths["journal"],
                    paths["snapshot"],
                    paths["retired_gate"],
                    paths["ledger"],
                    paths["d018_tx"],
                    paths["state"],
                )
                for path in evidence:
                    with self.subTest(path=path.name):
                        original = path.read_bytes()
                        if path == paths["ledger"]:
                            path.write_bytes(original + b" ")
                        else:
                            value = json.loads(original.decode("utf-8"))
                            value["tamper"] = True
                            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
                        try:
                            with self.assertRaises(SystemExit):
                                m9_budget.verify_unlimited_wall_clock_execution_ready()
                        finally:
                            path.write_bytes(original)

    def test_unlimited_generic_commands_are_zero_write_rejected_for_all_buckets(self) -> None:
        for bucket in ("none", "compatibility", "training", "physical_validation"):
            with self.subTest(bucket=bucket), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                state_path = root / "state.json"
                lock_path = root / "budget.lock"
                lock_path.write_text("lock\n", encoding="utf-8")
                state_path.write_text(
                    json.dumps(dict(self.limited_state(), wall_clock_policy=self.policy())) + "\n",
                    encoding="utf-8",
                )
                before = state_path.read_bytes()
                args = mock.Mock(
                    overlap_operation=False,
                    command=["/bin/true"],
                    cpu_bucket="none",
                    overlap_action=None,
                    structure_id=None,
                    forecast_bytes=0,
                    bucket=bucket,
                )
                with mock.patch.multiple(
                    m9_budget, STATE_PATH=state_path, LOCK_PATH=lock_path
                ), mock.patch.object(
                    m9_budget.subprocess, "Popen"
                ) as popen:
                    with self.assertRaisesRegex(SystemExit, "forbids generic commands"):
                        m9_budget.command_run(args)
                popen.assert_not_called()
                self.assertEqual(state_path.read_bytes(), before)

    def test_unlimited_overlap_requires_post_migration_execution_fact_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "state.json"
            workflow_path = root / "workflow.json"
            transaction_path = root / "transaction.json"
            lock_path = root / "budget.lock"
            state_path.write_text(
                json.dumps(dict(self.limited_state(), wall_clock_policy=self.policy())) + "\n",
                encoding="utf-8",
            )
            workflow_path.write_text(
                json.dumps({
                    "schema_version": "m9-overlap-workflow-state-v1",
                    "stage": "AUDIT_PASSED",
                    "apt_install_completed": True,
                    "hard_stopped": False,
                    "active_transaction": None,
                }) + "\n",
                encoding="utf-8",
            )
            transaction_path.write_text(
                json.dumps({"state": "SUCCESS_COMMITTED"}) + "\n", encoding="utf-8"
            )
            lock_path.write_text("lock\n", encoding="utf-8")
            before = (state_path.read_bytes(), workflow_path.read_bytes())
            args = mock.Mock(
                bucket="none",
                config=m9_budget.OVERLAP_CONTRACT.as_posix(),
                overlap_action="source_prepare",
                structure_id=None,
                cwd=None,
                log=None,
                command=None,
                cpu_bucket="overlap_build",
                forecast_bytes=1073741824,
            )
            with mock.patch.multiple(
                m9_budget,
                STATE_PATH=state_path,
                OVERLAP_WORKFLOW_STATE=workflow_path,
                OVERLAP_TRANSACTION=transaction_path,
                LOCK_PATH=lock_path,
            ), mock.patch.object(m9_budget.os, "geteuid", return_value=1000), mock.patch.object(
                m9_budget, "isolated_bootstrap_provenance", return_value={}
            ), mock.patch.object(
                m9_budget, "verify_unlimited_wall_clock_execution_ready", return_value={}
            ), mock.patch.object(
                m9_budget,
                "verify_unlimited_wall_clock_execution_fact_gate",
                side_effect=SystemExit("execution fact gate is missing"),
            ):
                with self.assertRaisesRegex(SystemExit, "execution fact gate"):
                    m9_budget.command_overlap_run(args)
            self.assertEqual((state_path.read_bytes(), workflow_path.read_bytes()), before)

    def test_overlap_rechecks_wall_mode_after_lock_acquisition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "state.json"
            workflow_path = root / "workflow.json"
            transaction_path = root / "transaction.json"
            lock_path = root / "budget.lock"
            limited = dict(self.limited_state(), overlap_storage_baseline={})
            unlimited = dict(limited, wall_clock_policy=self.policy())
            state_path.write_text(json.dumps(limited) + "\n", encoding="utf-8")
            workflow = {
                "schema_version": "m9-overlap-workflow-state-v1",
                "stage": "AUDIT_PASSED",
                "apt_install_completed": True,
                "hard_stopped": False,
                "active_transaction": None,
            }
            workflow_path.write_text(json.dumps(workflow) + "\n", encoding="utf-8")
            transaction_path.write_text('{"state":"SUCCESS_COMMITTED"}\n', encoding="utf-8")
            lock_path.write_text("lock\n", encoding="utf-8")
            args = mock.Mock(
                bucket="none", config=m9_budget.OVERLAP_CONTRACT.as_posix(),
                overlap_action="source_prepare", structure_id=None, cwd=None, log=None,
                command=None, cpu_bucket="overlap_build", forecast_bytes=1073741824,
            )
            real_flock = m9_budget.fcntl.flock

            def migrate_at_lock(handle: object, operation: int) -> None:
                real_flock(handle, operation)
                state_path.write_text(json.dumps(unlimited) + "\n", encoding="utf-8")

            with mock.patch.multiple(
                m9_budget, STATE_PATH=state_path, OVERLAP_WORKFLOW_STATE=workflow_path,
                OVERLAP_TRANSACTION=transaction_path, LOCK_PATH=lock_path,
            ), mock.patch.object(m9_budget.os, "geteuid", return_value=1000), mock.patch.object(
                m9_budget, "isolated_bootstrap_provenance", return_value={}
            ), mock.patch.object(m9_budget.fcntl, "flock", side_effect=migrate_at_lock), mock.patch.object(
                m9_budget, "verify_unlimited_wall_clock_execution_ready", return_value={}
            ), mock.patch.object(
                m9_budget, "verify_unlimited_wall_clock_execution_fact_gate",
                side_effect=SystemExit("execution fact gate is missing"),
            ):
                with self.assertRaisesRegex(SystemExit, "execution fact gate"):
                    m9_budget.command_overlap_run(args)
            self.assertEqual(json.loads(transaction_path.read_text())["state"], "SUCCESS_COMMITTED")

    def test_source_prepare_fact_scope_cannot_authorize_source_build(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = {name: root / name for name in ("state", "workflow", "transaction", "lock")}
            state = dict(self.limited_state(), wall_clock_policy=self.policy())
            paths["state"].write_text(json.dumps(state) + "\n", encoding="utf-8")
            paths["workflow"].write_text(json.dumps({
                "schema_version": "m9-overlap-workflow-state-v1", "stage": "SOURCES_PREPARED",
                "apt_install_completed": True, "hard_stopped": False, "active_transaction": None,
            }) + "\n", encoding="utf-8")
            paths["transaction"].write_text('{"state":"SUCCESS_COMMITTED"}\n', encoding="utf-8")
            paths["lock"].write_text("lock\n", encoding="utf-8")
            args = mock.Mock(
                bucket="none", config=m9_budget.OVERLAP_CONTRACT.as_posix(),
                overlap_action="source_build", structure_id=None, cwd=None, log=None,
                command=None, cpu_bucket="overlap_build", forecast_bytes=4294967296,
            )
            before = tuple(paths[name].read_bytes() for name in ("state", "workflow", "transaction"))
            with mock.patch.multiple(
                m9_budget, STATE_PATH=paths["state"], OVERLAP_WORKFLOW_STATE=paths["workflow"],
                OVERLAP_TRANSACTION=paths["transaction"], LOCK_PATH=paths["lock"],
            ), mock.patch.object(m9_budget.os, "geteuid", return_value=1000), mock.patch.object(
                m9_budget, "isolated_bootstrap_provenance", return_value={}
            ), mock.patch.object(
                m9_budget, "verify_unlimited_wall_clock_execution_ready", return_value={}
            ), mock.patch.object(
                m9_budget, "verify_unlimited_wall_clock_execution_fact_gate",
                return_value={"gate": {"scope": "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018"}},
            ):
                with self.assertRaisesRegex(SystemExit, "does not authorize this action"):
                    m9_budget.command_overlap_run(args)
            self.assertEqual(
                tuple(paths[name].read_bytes() for name in ("state", "workflow", "transaction")),
                before,
            )

    def test_generic_run_rechecks_unlimited_mode_inside_lock(self) -> None:
        for bucket in ("none", "compatibility", "training", "physical_validation"):
            with self.subTest(bucket=bucket), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                state_path = root / "state.json"
                lock_path = root / "budget.lock"
                limited = self.limited_state()
                unlimited = dict(limited, wall_clock_policy=self.policy())
                state_path.write_text(json.dumps(limited) + "\n", encoding="utf-8")
                lock_path.write_text("lock\n", encoding="utf-8")
                args = mock.Mock(
                    overlap_operation=False, command=["/bin/true"], cpu_bucket="none",
                    overlap_action=None, structure_id=None, forecast_bytes=0, bucket=bucket,
                )
                real_flock = m9_budget.fcntl.flock

                def migrate_at_lock(handle: object, operation: int) -> None:
                    real_flock(handle, operation)
                    state_path.write_text(json.dumps(unlimited) + "\n", encoding="utf-8")

                with mock.patch.multiple(
                    m9_budget, STATE_PATH=state_path, LOCK_PATH=lock_path
                ), mock.patch.object(
                    m9_budget.fcntl, "flock", side_effect=migrate_at_lock
                ), mock.patch.object(m9_budget.subprocess, "Popen") as popen:
                    with self.assertRaisesRegex(SystemExit, "forbids generic commands"):
                        m9_budget.command_run(args)
                popen.assert_not_called()

    def test_post_migration_execution_fact_gate_binds_complete_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stack, paths, _, _, _ = self.migration_fixture(Path(temporary))
            with stack, mock.patch.object(m9_budget.os, "geteuid", return_value=0):
                self.assertEqual(m9_budget.command_migrate_unlimited_wall_clock(mock.Mock()), 0)
                paths["execution_report"].write_text("# PASS\n", encoding="utf-8")
                report_sha = hashlib.sha256(paths["execution_report"].read_bytes()).hexdigest()
                verdict = {
                    "schema_version": "m9-unlimited-wall-clock-execution-audit-verdict-v1",
                    "decision_id": "D-018",
                    "verdict": "PASS",
                    "blocking": 0,
                    "non_blocking": 0,
                    "report_path": paths["execution_report"].as_posix(),
                    "report_sha256": report_sha,
                }
                paths["execution_verdict"].write_text(
                    json.dumps(verdict) + "\n", encoding="utf-8"
                )
                runtime = m9_budget.d018_execution_runtime_receipts()
                gate = {
                    "schema_version": "m9-unlimited-wall-clock-execution-gate-v1",
                    "decision_id": "D-018",
                    "status": "PASS",
                    "blocking": 0,
                    "non_blocking": 0,
                    "scope": "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018",
                    "verdict_path": paths["execution_verdict"].as_posix(),
                    "verdict_sha256": hashlib.sha256(
                        paths["execution_verdict"].read_bytes()
                    ).hexdigest(),
                    "runtime": runtime,
                    "d018_transaction_sha256": runtime["d018_transaction_sha256"],
                }
                paths["execution_gate"].write_text(
                    json.dumps(gate) + "\n", encoding="utf-8"
                )
                os.chown(paths["execution_gate"], 0, 1000)
                os.chmod(paths["execution_gate"], 0o640)
                result = m9_budget.verify_unlimited_wall_clock_execution_fact_gate()
                self.assertEqual(result["gate"], gate)
                original = paths["source_tx"].read_bytes()
                paths["source_tx"].write_bytes(original + b" ")
                try:
                    with self.assertRaisesRegex(SystemExit, "runtime drift"):
                        m9_budget.verify_unlimited_wall_clock_execution_fact_gate()
                finally:
                    paths["source_tx"].write_bytes(original)

    def test_d018_control_object_rejects_symlink_hardlink_and_writable_group(self) -> None:
        for kind in ("symlink", "hardlink", "group_writable"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                path = root / "gate.json"
                target = root / "target.json"
                target.write_text("{}\n", encoding="utf-8")
                if kind == "symlink":
                    path.symlink_to(target)
                elif kind == "hardlink":
                    os.link(target, path)
                else:
                    path.write_text("{}\n", encoding="utf-8")
                    os.chown(path, 0, 1000)
                    os.chmod(path, 0o660)
                with self.assertRaises(SystemExit):
                    m9_budget.read_d018_control_json(path)

    def test_d018_contract_preserves_all_non_wall_limits(self) -> None:
        budget_contract = json.loads(
            m9_budget.UNLIMITED_WALL_CLOCK_CONTRACT.read_text(encoding="utf-8")
        )
        unchanged = budget_contract["unchanged_limits"]
        self.assertEqual(unchanged["cpu_buckets_seconds"], m9_budget.CPU_LIMITS)
        self.assertEqual(unchanged["gpu_buckets_seconds"], m9_budget.GPU_LIMITS)
        self.assertEqual(unchanged["gpu_total_seconds"], m9_budget.GPU_TOTAL_LIMIT)
        self.assertEqual(unchanged["storage_total_bytes"], m9_budget.STORAGE_LIMIT)
        self.assertEqual(unchanged["project_audit_sublimit_bytes"], m9_budget.PROJECT_SUBLIMIT)
        self.assertEqual(unchanged["overlap_storage_sublimit_bytes"], m9_budget.OVERLAP_STORAGE_LIMIT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
