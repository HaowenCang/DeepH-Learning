#!/usr/bin/env python3
"""The only authorized executor for frozen M9 overlap-only calculations."""

from __future__ import annotations

import argparse
import importlib.abc
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

from m9_openmx_input import prepare_structure
from m9_overlap_common import (
    atomic_json,
    expected_structure_ids,
    file_sha256,
    hard_stop_workflow,
    load_contract,
    load_json,
    load_workflow_state,
    require_budget_context,
    runtime_path,
    save_workflow_state,
    verify_frozen_project_files,
    workflow_lock,
)
from m9_overlap_contract import expected_command, validate_preparse_outputs, validate_structure


class DeepHSourceLoader(importlib.abc.Loader):
    def __init__(self, fullname: str, path: Path, package: bool) -> None:
        self.fullname = fullname
        self.path = path
        self.package = package

    def create_module(self, spec: object) -> None:
        return None

    def exec_module(self, module: object) -> None:
        raw = self.path.read_bytes()
        module.__dict__["__deeph_source_sha256__"] = __import__("hashlib").sha256(raw).hexdigest()  # type: ignore[attr-defined]
        exec(compile(raw.decode("utf-8"), self.path.as_posix(), "exec", dont_inherit=True), module.__dict__)  # type: ignore[attr-defined]


class DeepHSourceFinder(importlib.abc.MetaPathFinder):
    def __init__(self, root: Path) -> None:
        self.root = root

    def find_spec(
        self, fullname: str, path: object = None, target: object = None
    ) -> object | None:
        if fullname != "deeph" and not fullname.startswith("deeph."):
            return None
        parts = fullname.split(".")
        package_init = self.root.joinpath(*parts, "__init__.py")
        module_path = self.root.joinpath(*parts).with_suffix(".py")
        if package_init.is_file():
            loader = DeepHSourceLoader(fullname, package_init, True)
            spec = importlib.util.spec_from_loader(
                fullname,
                loader,
                origin=package_init.as_posix(),
                is_package=True,
            )
            if spec is not None:
                spec.submodule_search_locations = [package_init.parent.as_posix()]
            return spec
        if module_path.is_file():
            loader = DeepHSourceLoader(fullname, module_path, False)
            return importlib.util.spec_from_loader(fullname, loader, origin=module_path.as_posix())
        return None


def require_budget_wrapper(bucket: str) -> dict[str, object]:
    context = require_budget_context(
        bucket,
        ("smoke_prepare", "smoke_run", "project")
        if bucket == "overlap_smoke"
        else ("batch_prepare", "batch_run"),
    )
    return context


def utc_now() -> str:
    import datetime as dt

    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def path_usage(path: Path) -> tuple[int, int]:
    apparent = 0
    allocated = 0
    if not path.exists():
        return apparent, allocated
    for root, _, files in os.walk(path, followlinks=False):
        for name in files:
            item = Path(root) / name
            if item.is_symlink():
                raise ValueError(f"symlink forbidden in run tree: {item}")
            stat = item.stat()
            apparent += stat.st_size
            allocated += stat.st_blocks * 512
    return apparent, allocated


def verify_deeph_source(contract: dict[str, object]) -> str:
    source = runtime_path(contract, "deeph_source")
    commit = subprocess.check_output(
        ["/usr/bin/git", "-C", os.fspath(source), "rev-parse", "HEAD"],
        text=True,
        encoding="utf-8",
    ).strip()
    dirty = subprocess.check_output(
        ["/usr/bin/git", "-C", os.fspath(source), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        encoding="utf-8",
    ).strip()
    if commit != "66703c532a6f633f4bbc8f94f75c8698a7f89859" or dirty:
        raise ValueError("DeepH v0.2.2 parser source identity changed")
    for path in source.rglob("*"):
        if path.is_symlink() or path.suffix == ".pyc" or path.name == "__pycache__":
            raise ValueError(f"DeepH parser tree contains forbidden cache/symlink: {path}")
    return commit


def import_deeph_parser_source_only(contract: dict[str, object]) -> object:
    source = runtime_path(contract, "deeph_source")
    for name in list(sys.modules):
        if name == "deeph" or name.startswith("deeph."):
            del sys.modules[name]
    finder = DeepHSourceFinder(source)
    sys.meta_path.insert(0, finder)
    try:
        from deeph.preprocess import openmx_parse_overlap
    finally:
        sys.meta_path.remove(finder)
    module = sys.modules.get("deeph.preprocess")
    origin = getattr(getattr(module, "__spec__", None), "origin", None)
    loader = getattr(getattr(module, "__spec__", None), "loader", None)
    if not isinstance(loader, DeepHSourceLoader) or origin != (
        source / "deeph/preprocess/__init__.py"
    ).as_posix():
        raise ValueError("DeepH parser was not loaded from frozen source-only loader")
    return openmx_parse_overlap


def prepare(structure_id: str, contract: dict[str, object], contract_hash: str) -> dict[str, object]:
    bucket = "overlap_smoke" if structure_id == "500" else "overlap_batch"
    require_budget_wrapper(bucket)
    return prepare_structure(structure_id, contract, contract_hash)


def verify_pre_run(
    structure_id: str,
    contract: dict[str, object],
    contract_hash: str,
) -> tuple[Path, dict[str, object], dict[str, object], str]:
    verify_frozen_project_files(contract)
    run_dir = runtime_path(contract, "run_root") / structure_id
    actual = sorted(
        path.relative_to(run_dir).as_posix()
        for path in run_dir.rglob("*")
        if path.is_file()
    )
    if actual != ["openmx.dat", "structure_mapping.json"]:
        raise ValueError(f"pre-run directory contains unauthorized files: {actual}")
    mapping = load_json(run_dir / "structure_mapping.json", "m9-openmx-structure-mapping-v1")
    build_manifest_path = runtime_path(contract, "build_manifest")
    build_manifest = load_json(build_manifest_path, "m9-openmx-overlap-build-manifest-v1")
    binary = runtime_path(contract, "openmx_binary")
    if binary.is_symlink() or not binary.is_file():
        raise ValueError("frozen OpenMX binary is missing or is a symlink")
    if mapping.get("contract_sha256") != contract_hash:
        raise ValueError("mapping/contract hash mismatch")
    if mapping.get("build_manifest_sha256") != file_sha256(build_manifest_path):
        raise ValueError("mapping/build manifest hash mismatch")
    if mapping.get("openmx_input", {}).get("sha256") != file_sha256(run_dir / "openmx.dat"):
        raise ValueError("OpenMX input changed after generation")
    if build_manifest.get("overlap_binary_sha256") != file_sha256(binary):
        raise ValueError("overlap binary/build manifest mismatch")
    if file_sha256(runtime_path(contract, "overlap_tree_manifest")) != build_manifest.get(
        "overlap_tree_manifest_sha256"
    ):
        raise ValueError("combined source/build manifest mismatch")
    basis = contract["basis"]
    assert isinstance(basis, dict)
    data_root = runtime_path(contract, "openmx_data")
    if file_sha256(data_root / "PAO/C6.0.pao") != basis["pao_sha256"]:
        raise ValueError("PAO changed after input generation")
    if file_sha256(data_root / "VPS/C_PBE19.vps") != basis["vps_sha256"]:
        raise ValueError("VPS changed after input generation")
    return run_dir, mapping, build_manifest, verify_deeph_source(contract)


def run_structure(structure_id: str, contract: dict[str, object], contract_hash: str) -> dict[str, object]:
    ids = expected_structure_ids(contract)
    if structure_id not in ids:
        raise ValueError("structure ID is outside frozen set")
    smoke = structure_id == "500"
    bucket = "overlap_smoke" if smoke else "overlap_batch"
    budget_context = require_budget_wrapper(bucket)
    with workflow_lock():
        state = load_workflow_state(contract)
        expected_stage = "SMOKE_INPUT_READY" if smoke else "BATCH_INPUT_READY"
        if state.get("stage") != expected_stage or state.get("hard_stopped"):
            raise ValueError(f"execution is not allowed at stage {state.get('stage')}")
        if state.get("active_structure_id") != structure_id or state.get("next_structure_id") != structure_id:
            raise ValueError("active/next structure ID does not match requested execution")
        run_dir, mapping, build_manifest, deeph_commit = verify_pre_run(
            structure_id, contract, contract_hash
        )
        before_apparent, before_allocated = path_usage(run_dir)
        host_vhdx = Path("/mnt/e/Laptop/WSL/ext4.vhdx")
        before_vhdx = host_vhdx.stat().st_size
        command = expected_command(contract)
        environment = dict(os.environ)
        environment["PATH"] = "/usr/sbin:/usr/bin:/sbin:/bin"
        environment["OMP_NUM_THREADS"] = "1"
        hdf_lib = runtime_path(contract, "hdf5_prefix") / "lib"
        environment["LD_LIBRARY_PATH"] = hdf_lib.as_posix()
        start_utc = utc_now()
        start_ns = time.monotonic_ns()
        with (run_dir / "openmx.std").open("wb") as stdout, (run_dir / "openmx.err").open(
            "wb"
        ) as stderr:
            completed = subprocess.run(
                command,
                cwd=run_dir,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                check=False,
            )
        end_ns = time.monotonic_ns()
        end_utc = utc_now()
        elapsed = (end_ns - start_ns) / 1_000_000_000.0
        if completed.returncode != 0:
            raise RuntimeError(f"overlap-only OpenMX exited {completed.returncode}")
        if not (run_dir / "openmx.out").is_file():
            raise ValueError("OpenMX merged openmx.out was not produced")
        validate_preparse_outputs(run_dir, contract)
        deeph_source = runtime_path(contract, "deeph_source")
        if verify_deeph_source(contract) != deeph_commit:
            raise ValueError("DeepH parser identity changed during OpenMX execution")
        openmx_parse_overlap = import_deeph_parser_source_only(contract)

        parsed_dir = run_dir / "parsed"
        parsed_dir.mkdir()
        openmx_parse_overlap(run_dir.as_posix(), parsed_dir.as_posix())
        after_payload_apparent, after_payload_allocated = path_usage(run_dir)
        after_payload_vhdx = host_vhdx.stat().st_size
        receipt: dict[str, object] = {
            "schema_version": "m9-overlap-execution-receipt-v1",
            "structure_id": structure_id,
            "contract_sha256": contract_hash,
            "build_manifest_sha256": file_sha256(runtime_path(contract, "build_manifest")),
            "binary_sha256": file_sha256(runtime_path(contract, "openmx_binary")),
            "overlap_tree_manifest_sha256": file_sha256(
                runtime_path(contract, "overlap_tree_manifest")
            ),
            "deeph_parser_commit": deeph_commit,
            "input_sha256": file_sha256(run_dir / "openmx.dat"),
            "mapping_sha256": file_sha256(run_dir / "structure_mapping.json"),
            "argv": command,
            "mpi_ranks": 1,
            "openmp_threads": 1,
            "cpu_bucket": bucket,
            "forecast_bytes": int(budget_context["forecast_bytes"]),
            "budget_transaction_id": str(budget_context["transaction_id"]),
            "start_utc": start_utc,
            "end_utc": end_utc,
            "elapsed_seconds": elapsed,
            "exit_code": completed.returncode,
            "stdout_sha256": file_sha256(run_dir / "openmx.std"),
            "stderr_sha256": file_sha256(run_dir / "openmx.err"),
            "merged_openmx_out_sha256": file_sha256(run_dir / "openmx.out"),
            "run_payload_increment_apparent_bytes": max(
                0, after_payload_apparent - before_apparent
            ),
            "run_payload_increment_allocated_bytes": max(
                0, after_payload_allocated - before_allocated
            ),
            "run_payload_vhdx_growth_bytes": max(0, after_payload_vhdx - before_vhdx),
        }
        atomic_json(run_dir / "execution_receipt.json", receipt)
        report = validate_structure(structure_id, contract, contract_hash)
        report_path = run_dir / "overlap_validation_report.json"
        atomic_json(report_path, report)

        completed_ids = list(state["completed_structure_ids"])
        if completed_ids != ids[: len(completed_ids)]:
            raise ValueError("completed structure IDs are not a strict prefix")
        completed_ids.append(structure_id)
        if completed_ids != ids[: len(completed_ids)]:
            raise ValueError("execution would violate ascending structure order")
        state["completed_structure_ids"] = completed_ids
        state["last_validation_report_sha256"] = file_sha256(report_path)
        state["active_structure_id"] = None
        state["active_input_sha256"] = None
        state["active_mapping_sha256"] = None
        if smoke:
            state["stage"] = "SMOKE_PASSED"
            state["smoke_elapsed_seconds"] = elapsed
            state["smoke_payload_increment_bytes"] = max(
                int(receipt["run_payload_increment_apparent_bytes"]),
                int(receipt["run_payload_increment_allocated_bytes"]),
                int(receipt["run_payload_vhdx_growth_bytes"]),
            )
            state["next_structure_id"] = ids[1]
        elif len(completed_ids) == len(ids):
            state["stage"] = "BATCH_COMPLETE"
            state["next_structure_id"] = None
        else:
            state["stage"] = "BATCH_RUNNING"
            state["next_structure_id"] = ids[len(completed_ids)]
        save_workflow_state(contract, state)
        return report


def compute_projection(
    contract: dict[str, object],
    state: dict[str, object],
    status: dict[str, object],
) -> dict[str, object]:
    if state.get("completed_structure_ids") != ["500"]:
        raise ValueError("projection requires exactly the validated smoke structure")
    elapsed = max(float(state["smoke_elapsed_seconds"]), 1.0)
    payload_storage = max(int(state["smoke_payload_increment_bytes"]), 1)
    budget = contract["budget"]
    assert isinstance(budget, dict)
    overhead = int(budget["per_structure_control_overhead_bytes"])
    per_structure_storage = payload_storage + overhead
    projected_cpu = math.ceil(elapsed * 450 * 1.25)
    projected_storage = math.ceil(per_structure_storage * 450 * 1.25)
    limits = budget["cpu_wall_subbudget_seconds"]
    batch_remaining = int(limits["full_450_structure_batch"]) - float(
        status["cpu_seconds"]["overlap_batch"]
    )
    reasons: list[str] = []
    if projected_cpu > batch_remaining:
        reasons.append("projected_overlap_batch_cpu")
    deadline_remaining = status.get("deadline_remaining_seconds")
    if deadline_remaining is not None and projected_cpu > float(deadline_remaining):
        reasons.append("projected_overall_wall_clock")
    storage_limit = int(budget["storage_increment_sublimit_bytes"])
    snap = status["storage"]
    for key in (
        "combined_apparent_bytes_since_overlap_baseline",
        "combined_allocated_bytes_since_overlap_baseline",
        "host_vhdx_growth_since_overlap_baseline_bytes",
    ):
        current = snap.get(key)
        if current is None or int(current) + projected_storage > storage_limit:
            reasons.append(f"projected_{key}")
    overall_limit = int(budget["overall_storage_limit_bytes"])
    for key in (
        "combined_apparent_bytes",
        "combined_allocated_bytes",
        "host_vhdx_growth_from_start_bytes",
    ):
        current = snap.get(key)
        if current is None or int(current) + projected_storage > overall_limit:
            reasons.append(f"projected_overall_{key}")
    return {
        "schema_version": "m9-overlap-projection-v1",
        "smoke_elapsed_seconds": elapsed,
        "smoke_payload_increment_bytes": payload_storage,
        "per_structure_control_overhead_bytes": overhead,
        "projected_per_structure_storage_bytes": per_structure_storage,
        "factor": 1.25,
        "structure_multiplier": 450,
        "projected_cpu_seconds": projected_cpu,
        "projected_storage_bytes": projected_storage,
        "batch_cpu_remaining_seconds": batch_remaining,
        "budget_status": status,
        "reasons": reasons,
        "status": "PASS" if not reasons else "HARD_STOP",
    }


def project_batch(contract: dict[str, object]) -> dict[str, object]:
    budget_context = require_budget_wrapper("overlap_smoke")
    with workflow_lock():
        state = load_workflow_state(contract)
        if state.get("stage") != "SMOKE_PASSED" or state.get("hard_stopped"):
            raise ValueError(f"projection is not allowed at stage {state.get('stage')}")
        status = budget_context.get("budget_status")
        if not isinstance(status, dict) or status.get("violations"):
            raise ValueError("project action lacks a clean bound budget snapshot")
        projection = compute_projection(contract, state, status)
        reasons = list(projection["reasons"])
        projection_path = runtime_path(contract, "manifest_root") / "overlap_batch_projection.json"
        atomic_json(projection_path, projection)
        if reasons:
            state["hard_stopped"] = True
            state["stage"] = "HARD_STOP"
            state["hard_stop_reason"] = reasons
            save_workflow_state(contract, state)
            raise RuntimeError(f"overlap batch projection failed: {reasons}")
        state["stage"] = "PROJECTION_PASSED"
        state["projection_sha256"] = file_sha256(projection_path)
        state["per_structure_forecast_bytes"] = math.ceil(
            int(projection["projected_storage_bytes"]) / 449
        )
        save_workflow_state(contract, state)
        return projection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("prepare", "run"):
        command = sub.add_parser(name)
        command.add_argument("--structure-id", required=True)
    sub.add_parser("project")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    contract, contract_hash = load_contract()
    try:
        if args.action == "prepare":
            result = prepare(str(args.structure_id), contract, contract_hash)
        elif args.action == "run":
            result = run_structure(str(args.structure_id), contract, contract_hash)
        else:
            result = project_batch(contract)
    except Exception as exc:
        hard_stop_workflow(contract, f"{type(exc).__name__}: {exc}")
        raise
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
