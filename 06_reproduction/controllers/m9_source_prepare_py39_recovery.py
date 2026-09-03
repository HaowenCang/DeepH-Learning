#!/usr/bin/env python3
"""One-shot recovery for the audited Python-3.9 source_prepare failure."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time


PROJECT_ROOT = Path("/mnt/e/Projects/Codex/DeepH")
REPRODUCTION = PROJECT_ROOT / "06_reproduction"
AUDITS = PROJECT_ROOT / "08_audits"
LINUX_ROOT = Path("/home/evan-williams/deeph-m9")
MANIFESTS = LINUX_ROOT / "manifests"
CONTROL_ROOT = Path("/root/deeph-m9-control")
FROZEN_PYTHON = LINUX_ROOT / "env/deeph-v022/bin/python3.9"

CONTRACT = REPRODUCTION / "manifests/m9_source_prepare_py39_recovery_contract.json"
FROZEN_HASHES = REPRODUCTION / "manifests/m9_source_prepare_py39_recovery_frozen_hashes.json"
WORK_PACKAGE = AUDITS / "M9_source_prepare_py39_recovery_work_package.md"
REPORT = AUDITS / "M9_source_prepare_py39_recovery_pid_reuse_targeted_reaudit.md"
VERDICT = AUDITS / "M9_source_prepare_py39_recovery_final_verdict.json"

GATE = CONTROL_ROOT / "source-prepare-py39-recovery-gate.json"
JOURNAL = CONTROL_ROOT / "source-prepare-py39-recovery-journal.json"
RECOVERY_TRANSACTION = CONTROL_ROOT / "source-prepare-py39-recovery-transaction.json"
FAILURE_TRANSACTION_SNAPSHOT = CONTROL_ROOT / "source-prepare-py39-failure-transaction.json"

LOCK = MANIFESTS / "budget.lock"
STATE = MANIFESTS / "budget_state.json"
WORKFLOW = MANIFESTS / "overlap_workflow_state.json"
LEDGER = MANIFESTS / "budget_ledger.jsonl"
FAILURE_TRANSACTION = MANIFESTS / "overlap_transaction.json"
STAGING = LINUX_ROOT / "software/openmx-overlap-build.staging"
RETIRED = LINUX_ROOT / (
    "software/openmx-overlap-build.failed-"
    "80e28da82f076f4f7b1811f5897216bd.retired"
)
CAPABILITY = MANIFESTS / (
    "overlap_capabilities/acc4548498ba22d8ce894b2725f89daf.consumed.json"
)
LAUNCHER_RECEIPT = MANIFESTS / (
    "overlap_capabilities/acc4548498ba22d8ce894b2725f89daf.launcher-receipt.json"
)

PHASES = (
    "PREPARED",
    "FAILURE_TX_SNAPSHOTTED",
    "STAGING_RETIRED",
    "LEDGER_COMMITTED",
    "STATE_COMMITTED",
    "WORKFLOW_COMMITTED",
    "SUCCESS_COMMITTED",
)
PHASE_INDEX = {phase: index for index, phase in enumerate(PHASES)}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def exact_open_receipt(
    descriptor: int,
    path: Path,
    *,
    uid: int,
    gid: int,
    mode: int,
) -> tuple[dict[str, object], bytes]:
    """Read and bind an already-open descriptor to its current path identity."""
    before = os.fstat(descriptor)
    payload_chunks: list[bytes] = []
    offset = 0
    while offset < before.st_size:
        chunk = os.pread(descriptor, min(1024 * 1024, before.st_size - offset), offset)
        if not chunk:
            raise ValueError(f"short stable descriptor read: {path}")
        payload_chunks.append(chunk)
        offset += len(chunk)
    after = os.fstat(descriptor)
    linked = os.lstat(path)
    fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
    if (
        any(getattr(before, key) != getattr(after, key) for key in fields)
        or any(getattr(after, key) != getattr(linked, key) for key in fields)
        or not stat.S_ISREG(after.st_mode)
        or after.st_nlink != 1
        or after.st_uid != uid
        or after.st_gid != gid
        or stat.S_IMODE(after.st_mode) != mode
    ):
        raise ValueError(f"stable regular metadata mismatch: {path}")
    payload = b"".join(payload_chunks)
    if len(payload) != after.st_size:
        raise ValueError(f"stable regular byte count mismatch: {path}")
    return {
        "path": path.as_posix(),
        "sha256": sha256_bytes(payload),
        "bytes": len(payload),
        "uid": after.st_uid,
        "gid": after.st_gid,
        "mode": stat.S_IMODE(after.st_mode),
        "nlink": after.st_nlink,
        "st_dev": after.st_dev,
        "st_ino": after.st_ino,
    }, payload


def exact_receipt(path: Path, *, uid: int, gid: int, mode: int) -> tuple[dict[str, object], bytes]:
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        return exact_open_receipt(descriptor, path, uid=uid, gid=gid, mode=mode)
    finally:
        os.close(descriptor)


def isolated_bootstrap() -> dict[str, object]:
    executable = Path(sys.executable).resolve(strict=True)
    if (
        executable != FROZEN_PYTHON.resolve(strict=True)
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or os.geteuid() != 0
    ):
        raise SystemExit("recovery requires root frozen Python -I -S -B")
    return {
        "python_executable": executable.as_posix(),
        "isolated": True,
        "no_site": True,
        "dont_write_bytecode": True,
    }


def tree_inventory(root: Path) -> dict[str, object]:
    linked = os.lstat(root)
    if not stat.S_ISDIR(linked.st_mode) or stat.S_ISLNK(linked.st_mode):
        raise ValueError("staging root is not a real directory")
    records: list[dict[str, object]] = [{
        "path": ".",
        "mode": stat.S_IMODE(linked.st_mode),
        "uid": linked.st_uid,
        "gid": linked.st_gid,
        "nlink": linked.st_nlink,
        "size": linked.st_size,
        "type": "directory",
    }]
    apparent = 0
    allocated = linked.st_blocks * 512
    directories = 1
    regular_files = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        info = os.lstat(path)
        relative = path.relative_to(root).as_posix()
        base: dict[str, object] = {
            "path": relative,
            "mode": stat.S_IMODE(info.st_mode),
            "uid": info.st_uid,
            "gid": info.st_gid,
            "nlink": info.st_nlink,
            "size": info.st_size,
        }
        allocated += info.st_blocks * 512
        if stat.S_ISDIR(info.st_mode):
            base["type"] = "directory"
            directories += 1
        elif stat.S_ISREG(info.st_mode):
            base["type"] = "regular"
            with path.open("rb") as handle:
                digest = hashlib.sha256()
                while block := handle.read(8 * 1024 * 1024):
                    digest.update(block)
            base["sha256"] = digest.hexdigest()
            apparent += info.st_size
            regular_files += 1
        else:
            raise ValueError(f"staging contains a link or special object: {relative}")
        records.append(base)
    return {
        "root": root.as_posix(),
        "directories": directories,
        "regular_files": regular_files,
        "records": len(records),
        "apparent_bytes": apparent,
        "allocated_bytes": allocated,
        "inventory_sha256": sha256_bytes(canonical_bytes(records)),
    }


def atomic_bytes(path: Path, payload: bytes, *, uid: int, gid: int, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        linked = os.lstat(temporary)
        if (
            stat.S_ISLNK(linked.st_mode)
            or not stat.S_ISREG(linked.st_mode)
            or linked.st_nlink != 1
        ):
            raise ValueError("durable temporary is not a single regular file")
        existing = temporary.read_bytes()
        metadata_ready = (
            linked.st_uid == uid
            and linked.st_gid == gid
            and stat.S_IMODE(linked.st_mode) == mode
        )
        root_empty = linked.st_uid == 0 and linked.st_gid == 0 and len(existing) == 0
        if not root_empty and not (metadata_ready and payload.startswith(existing)):
            raise ValueError("durable temporary content or metadata mismatch")
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_TRUNC | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
    else:
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
            mode,
        )
    try:
        os.fchown(descriptor, uid, gid)
        os.fchmod(descriptor, mode)
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short durable write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    _, actual = exact_receipt(path, uid=uid, gid=gid, mode=mode)
    if actual != payload:
        raise ValueError(f"durable target mismatch: {path}")


def atomic_json(path: Path, value: object, *, uid: int, gid: int, mode: int) -> None:
    atomic_bytes(path, pretty_bytes(value), uid=uid, gid=gid, mode=mode)


def load_contract() -> tuple[dict[str, object], bytes]:
    payload = CONTRACT.read_bytes()
    value = json.loads(payload.decode("utf-8"))
    if value.get("schema_version") != "m9-source-prepare-py39-recovery-contract-v1":
        raise ValueError("recovery contract schema mismatch")
    return value, payload


def verify_frozen() -> tuple[dict[str, object], bytes]:
    payload = FROZEN_HASHES.read_bytes()
    value = json.loads(payload.decode("utf-8"))
    files = value.get("files")
    if (
        value.get("schema_version") != "m9-source-prepare-py39-recovery-frozen-v1"
        or not isinstance(files, dict)
    ):
        raise ValueError("recovery frozen manifest schema mismatch")
    for raw_path, expected in files.items():
        path = Path(raw_path)
        if sha256_bytes(path.read_bytes()) != expected:
            raise ValueError(f"recovery frozen member mismatch: {path}")
    return value, payload


def runtime_receipts(contract: dict[str, object]) -> dict[str, dict[str, object]]:
    expected = contract["expected_runtime"]
    if not isinstance(expected, dict):
        raise ValueError("expected runtime map is invalid")
    result: dict[str, dict[str, object]] = {}
    for name, value in expected.items():
        if not isinstance(value, dict):
            raise ValueError(f"runtime contract entry is invalid: {name}")
        path = Path(str(value["path"]))
        receipt, _ = exact_receipt(
            path,
            uid=int(value["uid"]), gid=int(value["gid"]), mode=int(value["mode"]),
        )
        checked = ["sha256", "bytes", "uid", "gid", "mode", "nlink"]
        checked.extend(key for key in ("st_dev", "st_ino") if key in value)
        for key in checked:
            if receipt[key] != value[key]:
                raise ValueError(f"runtime receipt mismatch: {name}.{key}")
        result[name] = receipt
    return result


def verify_failure_semantics(contract: dict[str, object]) -> None:
    transaction = json.loads(FAILURE_TRANSACTION.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    workflow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    capability = json.loads(CAPABILITY.read_text(encoding="utf-8"))
    receipt = json.loads(LAUNCHER_RECEIPT.read_text(encoding="utf-8"))
    if (
        transaction.get("transaction_id") != contract["failure_transaction_id"]
        or transaction.get("state") != "FAILED_COMMITTED"
        or transaction.get("action") != "source_prepare"
        or not isinstance(transaction.get("child_pid"), int)
        or int(transaction["child_pid"]) <= 0
        or not isinstance(transaction.get("exit_code"), int)
        or isinstance(transaction.get("exit_code"), bool)
        or int(transaction["exit_code"]) == 0
        or transaction.get("timed_out") is not False
        or not isinstance(transaction.get("start_utc"), str)
        or not isinstance(transaction.get("end_utc"), str)
        or not isinstance(transaction.get("failure_utc"), str)
        or not isinstance(transaction.get("elapsed_seconds"), (int, float))
        or float(transaction["elapsed_seconds"]) < 0.0
        or transaction.get("reasons") != ["overlap_command_failed"]
        or not state.get("hard_stopped")
        or state.get("active_overlap_transaction") is not None
        or workflow.get("stage") != "HARD_STOP"
        or not workflow.get("hard_stopped")
        or workflow.get("active_transaction") is not None
        or capability.get("state") != "CONSUMED"
        or capability.get("transaction_id") != contract["failure_transaction_id"]
        or capability.get("child_pid") != transaction.get("child_pid")
        or receipt.get("status") != "FAIL"
        or receipt.get("transaction_id") != contract["failure_transaction_id"]
    ):
        raise ValueError("formal Python-3.9 failure semantics mismatch")


def process_matches_argv(
    pid: int,
    expected_argv: list[object],
    *,
    proc_root: Path = Path("/proc"),
) -> bool:
    """Distinguish the historical launcher from an unrelated reused PID."""
    if (
        pid <= 0
        or not expected_argv
        or any(not isinstance(item, str) or "\0" in item for item in expected_argv)
    ):
        raise ValueError("historical launcher identity is invalid")
    cmdline = proc_root / str(pid) / "cmdline"
    try:
        payload = cmdline.read_bytes()
    except FileNotFoundError:
        return False
    expected = b"\0".join(str(item).encode("utf-8") for item in expected_argv) + b"\0"
    return payload == expected


def verify_immutable_runtime(contract: dict[str, object]) -> None:
    expected = contract["expected_runtime"]
    if not isinstance(expected, dict):
        raise ValueError("expected runtime map is invalid")
    for name, value in expected.items():
        if name in {"state", "workflow", "ledger"}:
            continue
        if not isinstance(value, dict):
            raise ValueError(f"immutable runtime entry is invalid: {name}")
        receipt, _ = exact_receipt(
            Path(str(value["path"])),
            uid=int(value["uid"]), gid=int(value["gid"]), mode=int(value["mode"]),
        )
        for key in ("sha256", "bytes", "uid", "gid", "mode", "nlink", "st_dev", "st_ino"):
            if key in value and receipt[key] != value[key]:
                raise ValueError(f"immutable runtime drift: {name}.{key}")


def verify_lock_binding(
    descriptor: int,
    contract: dict[str, object],
    gate_runtime: dict[str, object],
) -> dict[str, object]:
    expected_runtime = contract["expected_runtime"]
    if not isinstance(expected_runtime, dict):
        raise ValueError("expected runtime map is invalid")
    expected = expected_runtime.get("lock")
    gated = gate_runtime.get("lock")
    if not isinstance(expected, dict) or not isinstance(gated, dict):
        raise ValueError("budget lock is absent from contract or gate")
    receipt, payload = exact_open_receipt(
        descriptor,
        LOCK,
        uid=int(expected["uid"]),
        gid=int(expected["gid"]),
        mode=int(expected["mode"]),
    )
    if receipt != expected or receipt != gated or sha256_bytes(payload) != expected["sha256"]:
        raise ValueError("budget lock identity differs from contract or recovery gate")
    return receipt


def verify_ledger(contract: dict[str, object]) -> bytes:
    payload = LEDGER.read_bytes()
    ledger = contract["ledger"]
    if not isinstance(ledger, dict):
        raise ValueError("ledger contract is invalid")
    if (
        len(payload) != int(ledger["bytes"])
        or sha256_bytes(payload) != ledger["sha256"]
        or sha256_bytes(payload[: int(ledger["prefix_bytes"])]) != ledger["prefix_sha256"]
        or sha256_bytes(payload[int(ledger["prefix_bytes"]) :]) != ledger["failure_suffix_sha256"]
    ):
        raise ValueError("formal ledger prefix/failure suffix mismatch")
    return payload


def expected_tree_inventory(contract: dict[str, object]) -> dict[str, object]:
    value = contract["staging_inventory"]
    if not isinstance(value, dict):
        raise ValueError("staging inventory contract is invalid")
    keys = {
        "root", "directories", "regular_files", "records",
        "apparent_bytes", "allocated_bytes", "inventory_sha256",
    }
    return {key: value[key] for key in keys}


def verify_failure_side_invariants(contract: dict[str, object]) -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    budget = contract["budget_invariants"]
    if not isinstance(budget, dict):
        raise ValueError("budget invariant contract is invalid")
    adjustments = state.get("cpu_adjustments")
    gpu = state.get("gpu_seconds")
    cpu = state.get("cpu_seconds")
    wall = state.get("wall_clock_policy")
    if (
        not isinstance(adjustments, list)
        or len(adjustments) != 1
        or not isinstance(gpu, dict)
        or not isinstance(cpu, dict)
        or not isinstance(wall, dict)
        or float(cpu.get("overlap_build", -1)) != float(budget["raw_overlap_build_seconds"])
        or float(adjustments[0].get("credited_seconds", -1)) != float(budget["credited_seconds"])
        or wall.get("mode") != budget["wall_clock_mode"]
        or float(gpu.get("compatibility", -1)) != float(budget["gpu_compatibility_seconds"])
        or float(gpu.get("training", -1)) != float(budget["gpu_training_seconds"])
        or float(gpu.get("physical_validation", -1))
        != float(budget["gpu_physical_validation_seconds"])
    ):
        raise ValueError("budget/history invariant mismatch")
    for raw in contract["products_required_absent"]:
        if os.path.lexists(str(raw)):
            raise ValueError(f"forbidden source/build product exists: {raw}")
    active_capability = CAPABILITY.with_name("acc4548498ba22d8ce894b2725f89daf.json")
    if os.path.lexists(active_capability) or os.path.lexists(RETIRED):
        raise ValueError("active capability or retired target pre-exists")
    makefile = STAGING / "openmx3.9/source/makefile"
    if sha256_bytes(makefile.read_bytes()) != contract["staging_inventory"]["makefile_sha256"]:
        raise ValueError("failure makefile evidence mismatch")
    transaction = json.loads(FAILURE_TRANSACTION.read_text(encoding="utf-8"))
    capability = json.loads(CAPABILITY.read_text(encoding="utf-8"))
    child_pid = int(transaction.get("child_pid", -1))
    launcher_argv = capability.get("launcher_argv")
    if not isinstance(launcher_argv, list):
        raise ValueError("historical launcher argv is absent")
    if process_matches_argv(child_pid, launcher_argv):
        raise ValueError("failed source_prepare child is still alive")


def build_gate_payload(recovery_utc: str) -> dict[str, object]:
    contract, contract_bytes = load_contract()
    _, frozen_bytes = verify_frozen()
    runtime = runtime_receipts(contract)
    verify_failure_semantics(contract)
    ledger = verify_ledger(contract)
    inventory = tree_inventory(STAGING)
    if inventory != expected_tree_inventory(contract):
        raise ValueError("formal staging inventory mismatch")
    verify_failure_side_invariants(contract)
    verdict_bytes = VERDICT.read_bytes()
    report_bytes = REPORT.read_bytes()
    verdict = json.loads(verdict_bytes.decode("utf-8"))
    if (
        verdict.get("schema_version") != "m9-source-prepare-py39-recovery-verdict-v1"
        or verdict.get("decision_id") != "D-018"
        or verdict.get("status") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("report_path") != REPORT.as_posix()
        or verdict.get("report_sha256") != sha256_bytes(report_bytes)
        or verdict.get("work_package_path") != WORK_PACKAGE.as_posix()
        or verdict.get("work_package_sha256") != sha256_bytes(WORK_PACKAGE.read_bytes())
        or verdict.get("frozen_hashes_path") != FROZEN_HASHES.as_posix()
        or verdict.get("frozen_hashes_sha256") != sha256_bytes(frozen_bytes)
    ):
        raise ValueError("recovery independent verdict binding mismatch")
    return {
        "schema_version": "m9-source-prepare-py39-recovery-gate-v1",
        "decision_id": "D-018",
        "scope": "RECOVER_ONLY_M9_SP_PY39_B01",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
        "recovery_id": contract["recovery_id"],
        "recovery_utc": recovery_utc,
        "contract_path": CONTRACT.as_posix(),
        "contract_sha256": sha256_bytes(contract_bytes),
        "frozen_hashes_path": FROZEN_HASHES.as_posix(),
        "frozen_hashes_sha256": sha256_bytes(frozen_bytes),
        "verdict_path": VERDICT.as_posix(),
        "verdict_sha256": sha256_bytes(verdict_bytes),
        "report_path": REPORT.as_posix(),
        "report_sha256": sha256_bytes(report_bytes),
        "work_package_path": WORK_PACKAGE.as_posix(),
        "work_package_sha256": sha256_bytes(WORK_PACKAGE.read_bytes()),
        "runtime": runtime,
        "ledger_sha256": sha256_bytes(ledger),
        "staging_inventory": inventory,
        "pre_state": json.loads(STATE.read_text(encoding="utf-8")),
        "pre_workflow": json.loads(WORKFLOW.read_text(encoding="utf-8")),
        "python_bootstrap": isolated_bootstrap(),
    }


def create_gate() -> int:
    if any(os.path.lexists(path) for path in (GATE, JOURNAL, RECOVERY_TRANSACTION)):
        raise SystemExit("recovery gate or transaction already exists")
    recovery_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = build_gate_payload(recovery_utc)
    atomic_json(GATE, payload, uid=0, gid=0, mode=0o600)
    print(json.dumps({"status": "py39_recovery_gate_created", "sha256": sha256_bytes(GATE.read_bytes())}, sort_keys=True))
    return 0


def load_gate() -> tuple[dict[str, object], dict[str, object]]:
    gate_receipt, gate_bytes = exact_receipt(GATE, uid=0, gid=0, mode=0o600)
    gate = json.loads(gate_bytes.decode("utf-8"))
    contract, contract_bytes = load_contract()
    _, frozen_bytes = verify_frozen()
    verdict_bytes = VERDICT.read_bytes()
    report_bytes = REPORT.read_bytes()
    work_package_bytes = WORK_PACKAGE.read_bytes()
    verdict = json.loads(verdict_bytes.decode("utf-8"))
    if (
        gate.get("schema_version") != "m9-source-prepare-py39-recovery-gate-v1"
        or gate.get("decision_id") != "D-018"
        or gate.get("scope") != "RECOVER_ONLY_M9_SP_PY39_B01"
        or gate.get("status") != "PASS"
        or int(gate.get("blocking", -1)) != 0
        or int(gate.get("non_blocking", -1)) != 0
        or gate.get("recovery_id") != contract["recovery_id"]
        or gate.get("contract_path") != CONTRACT.as_posix()
        or gate.get("contract_sha256") != sha256_bytes(contract_bytes)
        or gate.get("frozen_hashes_path") != FROZEN_HASHES.as_posix()
        or gate.get("frozen_hashes_sha256") != sha256_bytes(frozen_bytes)
        or gate.get("verdict_path") != VERDICT.as_posix()
        or gate.get("verdict_sha256") != sha256_bytes(verdict_bytes)
        or gate.get("report_path") != REPORT.as_posix()
        or gate.get("report_sha256") != sha256_bytes(report_bytes)
        or gate.get("work_package_path") != WORK_PACKAGE.as_posix()
        or gate.get("work_package_sha256") != sha256_bytes(work_package_bytes)
        or verdict.get("schema_version") != "m9-source-prepare-py39-recovery-verdict-v1"
        or verdict.get("decision_id") != "D-018"
        or verdict.get("status") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("report_path") != REPORT.as_posix()
        or verdict.get("report_sha256") != sha256_bytes(report_bytes)
        or verdict.get("work_package_path") != WORK_PACKAGE.as_posix()
        or verdict.get("work_package_sha256") != sha256_bytes(work_package_bytes)
        or verdict.get("frozen_hashes_path") != FROZEN_HASHES.as_posix()
        or verdict.get("frozen_hashes_sha256") != sha256_bytes(frozen_bytes)
        or gate.get("python_bootstrap") != isolated_bootstrap()
    ):
        raise ValueError("recovery gate authorization binding mismatch")
    return gate, gate_receipt


def append_event_exact(prefix: bytes, event_line: bytes) -> dict[str, object]:
    current = LEDGER.read_bytes()
    target = prefix + event_line
    if current == target:
        receipt, payload = exact_receipt(LEDGER, uid=1000, gid=1000, mode=0o644)
        if payload != target:
            raise ValueError("ledger target changed during receipt capture")
        return receipt
    if not target.startswith(current) or len(current) < len(prefix):
        raise ValueError("ledger is not an authorized recovery-event prefix")
    descriptor = os.open(
        LEDGER,
        os.O_WRONLY | os.O_APPEND | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        linked = os.fstat(descriptor)
        if (
            not stat.S_ISREG(linked.st_mode)
            or linked.st_uid != 1000
            or linked.st_gid != 1000
            or stat.S_IMODE(linked.st_mode) != 0o644
            or linked.st_nlink != 1
        ):
            raise ValueError("ledger append target metadata mismatch")
        remaining = target[len(current) :]
        view = memoryview(remaining)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short ledger append")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    final = LEDGER.read_bytes()
    if final != target:
        raise ValueError("ledger recovery event commit mismatch")
    receipt, payload = exact_receipt(LEDGER, uid=1000, gid=1000, mode=0o644)
    if payload != target:
        raise ValueError("ledger target changed during receipt capture")
    return receipt


def phase_record(base: dict[str, object], phase: str) -> dict[str, object]:
    value = dict(base)
    value["state"] = phase
    return value


def recover() -> int:
    gate, gate_receipt = load_gate()
    contract, _ = load_contract()
    descriptor = os.open(LOCK, os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        bootstrap = isolated_bootstrap()
        pre_runtime = gate["runtime"]
        if not isinstance(pre_runtime, dict):
            raise ValueError("gate runtime is invalid")
        verify_lock_binding(descriptor, contract, pre_runtime)
        verify_immutable_runtime(contract)
        recovery_id = str(gate["recovery_id"])
        base = {
            "schema_version": "m9-source-prepare-py39-recovery-transaction-v1",
            "decision_id": "D-018",
            "recovery_id": recovery_id,
            "failure_transaction_id": contract["failure_transaction_id"],
            "gate": gate_receipt,
            "python_bootstrap": bootstrap,
            "pre_runtime": pre_runtime,
            "staging_inventory": gate["staging_inventory"],
            "retired_path": RETIRED.as_posix(),
            "recovery_utc": gate["recovery_utc"],
        }
        inherited_ledger: dict[str, object] | None = None
        inherited_state: dict[str, object] | None = None
        inherited_workflow: dict[str, object] | None = None
        if os.path.lexists(JOURNAL):
            _, journal_bytes = exact_receipt(JOURNAL, uid=0, gid=0, mode=0o600)
            journal = json.loads(journal_bytes.decode("utf-8"))
            if any(journal.get(key) != value for key, value in base.items()):
                raise ValueError("recovery journal context mismatch")
            journal_phase = journal.get("state")
            if journal_phase not in PHASE_INDEX:
                raise ValueError("recovery journal phase is invalid")
            transaction: dict[str, object] | None = None
            transaction_bytes: bytes | None = None
            if os.path.lexists(RECOVERY_TRANSACTION):
                _, transaction_bytes = exact_receipt(
                    RECOVERY_TRANSACTION, uid=0, gid=0, mode=0o600
                )
                transaction = json.loads(transaction_bytes.decode("utf-8"))
                if any(transaction.get(key) != value for key, value in base.items()):
                    raise ValueError("recovery transaction context mismatch")
                transaction_phase = transaction.get("state")
                if transaction_phase not in PHASE_INDEX:
                    raise ValueError("recovery transaction phase is invalid")
                journal_index = PHASE_INDEX[str(journal_phase)]
                transaction_index = PHASE_INDEX[str(transaction_phase)]
                allowed_pair = (
                    journal_index == transaction_index
                    or (journal_index == transaction_index + 1 and journal_index <= PHASE_INDEX["WORKFLOW_COMMITTED"])
                    or (
                        journal_phase == "WORKFLOW_COMMITTED"
                        and transaction_phase == "SUCCESS_COMMITTED"
                    )
                )
                if not allowed_pair:
                    raise ValueError("recovery journal/transaction phase pair is invalid")
            elif journal_phase != "PREPARED":
                raise ValueError("only PREPARED journal may precede recovery transaction")

            records = [journal] + ([transaction] if transaction is not None else [])

            def inherit_post_receipt(
                key: str,
                minimum_phase: str,
                path: Path,
            ) -> dict[str, object] | None:
                candidates: list[dict[str, object]] = []
                for record in records:
                    if record is None or PHASE_INDEX[str(record["state"])] < PHASE_INDEX[minimum_phase]:
                        continue
                    candidate = record.get(key)
                    if not isinstance(candidate, dict):
                        raise ValueError(f"{key} is absent from committed recovery phase")
                    candidates.append(candidate)
                if not candidates:
                    return None
                if any(candidate != candidates[0] for candidate in candidates[1:]):
                    raise ValueError(f"{key} changed between committed recovery phases")
                receipt, _ = exact_receipt(path, uid=1000, gid=1000, mode=0o644)
                if receipt != candidates[0]:
                    raise ValueError(f"{key} runtime identity drift after committed phase")
                return candidates[0]

            inherited_ledger = inherit_post_receipt(
                "post_ledger", "LEDGER_COMMITTED", LEDGER
            )
            inherited_state = inherit_post_receipt(
                "post_state", "STATE_COMMITTED", STATE
            )
            inherited_workflow = inherit_post_receipt(
                "post_workflow", "WORKFLOW_COMMITTED", WORKFLOW
            )

            terminal = None
            if journal_phase == "SUCCESS_COMMITTED":
                terminal = journal
                if transaction_bytes != journal_bytes:
                    raise ValueError("terminal recovery transaction/journal mismatch")
            elif transaction is not None and transaction.get("state") == "SUCCESS_COMMITTED":
                terminal = transaction
            if terminal is not None:
                if os.path.lexists(STAGING) or not RETIRED.is_dir() or RETIRED.is_symlink():
                    raise ValueError("terminal staging retirement mismatch")
                retired_inventory = tree_inventory(RETIRED)
                normalized = dict(retired_inventory)
                normalized["root"] = STAGING.as_posix()
                if normalized != expected_tree_inventory(contract):
                    raise ValueError("terminal retired inventory mismatch")
                if journal_phase != "SUCCESS_COMMITTED":
                    verify_lock_binding(descriptor, contract, pre_runtime)
                    atomic_json(JOURNAL, terminal, uid=0, gid=0, mode=0o600)
                verify_lock_binding(descriptor, contract, pre_runtime)
                print(json.dumps({"status": "source_prepare_py39_already_recovered", "recovery_id": recovery_id}, sort_keys=True))
                return 0
        else:
            if os.path.lexists(RECOVERY_TRANSACTION):
                raise ValueError("recovery transaction exists without journal")
            current_runtime = runtime_receipts(contract)
            if current_runtime != pre_runtime:
                raise ValueError("formal failure runtime differs from recovery gate")
            verify_failure_semantics(contract)
            verify_ledger(contract)
            verify_failure_side_invariants(contract)
            if tree_inventory(STAGING) != expected_tree_inventory(contract):
                raise ValueError("pre-recovery staging inventory mismatch")
            journal = phase_record(base, "PREPARED")
            verify_lock_binding(descriptor, contract, pre_runtime)
            atomic_json(JOURNAL, journal, uid=0, gid=0, mode=0o600)
            verify_lock_binding(descriptor, contract, pre_runtime)
            atomic_json(RECOVERY_TRANSACTION, journal, uid=0, gid=0, mode=0o600)

        failure_receipt = pre_runtime["failure_transaction"]
        if not isinstance(failure_receipt, dict):
            raise ValueError("failure transaction receipt is invalid")
        if os.path.lexists(FAILURE_TRANSACTION_SNAPSHOT):
            snapshot_receipt, snapshot_bytes = exact_receipt(
                FAILURE_TRANSACTION_SNAPSHOT, uid=0, gid=0, mode=0o600
            )
            if snapshot_bytes != FAILURE_TRANSACTION.read_bytes():
                raise ValueError(f"failure transaction snapshot mismatch: {snapshot_receipt}")
        else:
            verify_lock_binding(descriptor, contract, pre_runtime)
            atomic_bytes(
                FAILURE_TRANSACTION_SNAPSHOT,
                FAILURE_TRANSACTION.read_bytes(),
                uid=0, gid=0, mode=0o600,
            )
        journal = phase_record(base, "FAILURE_TX_SNAPSHOTTED")
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(JOURNAL, journal, uid=0, gid=0, mode=0o600)
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(RECOVERY_TRANSACTION, journal, uid=0, gid=0, mode=0o600)

        source_linked = os.path.lexists(STAGING)
        retired_linked = os.path.lexists(RETIRED)
        if (source_linked and STAGING.is_symlink()) or (retired_linked and RETIRED.is_symlink()):
            raise ValueError("staging retirement path is a symlink")
        source_exists = source_linked and STAGING.is_dir()
        retired_exists = retired_linked and RETIRED.is_dir()
        if source_exists and not retired_exists:
            if tree_inventory(STAGING) != expected_tree_inventory(contract):
                raise ValueError("staging changed before retirement")
            verify_lock_binding(descriptor, contract, pre_runtime)
            os.replace(STAGING, RETIRED)
            directory = os.open(RETIRED.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        elif source_exists or not retired_exists:
            raise ValueError("staging retirement state is ambiguous")
        retired_inventory = tree_inventory(RETIRED)
        normalized = dict(retired_inventory)
        normalized["root"] = STAGING.as_posix()
        if normalized != expected_tree_inventory(contract):
            raise ValueError("retired staging inventory mismatch")
        journal = phase_record(base, "STAGING_RETIRED")
        journal["retired_inventory"] = retired_inventory
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(JOURNAL, journal, uid=0, gid=0, mode=0o600)
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(RECOVERY_TRANSACTION, journal, uid=0, gid=0, mode=0o600)

        current_ledger = LEDGER.read_bytes()
        event = {
            "event": "OVERLAP_SOURCE_PREPARE_PY39_RECOVERY",
            "event_id": recovery_id + ":recovery",
            "recovery_id": recovery_id,
            "failure_transaction_id": contract["failure_transaction_id"],
            "failure_transaction_sha256": failure_receipt["sha256"],
            "retired_path": RETIRED.as_posix(),
            "staging_inventory_sha256": contract["staging_inventory"]["inventory_sha256"],
            "utc": gate["recovery_utc"],
        }
        event_line = canonical_bytes(event) + b"\n"
        original_ledger = current_ledger[: int(contract["ledger"]["bytes"])]
        if (
            len(original_ledger) != int(contract["ledger"]["bytes"])
            or sha256_bytes(original_ledger) != contract["ledger"]["sha256"]
        ):
            raise ValueError("ledger recovery prefix mismatch")
        verify_lock_binding(descriptor, contract, pre_runtime)
        ledger_receipt = append_event_exact(original_ledger, event_line)
        if inherited_ledger is not None and ledger_receipt != inherited_ledger:
            raise ValueError("committed ledger receipt cannot be rebound")
        if inherited_ledger is not None:
            ledger_receipt = inherited_ledger
        journal = phase_record(base, "LEDGER_COMMITTED")
        journal["ledger_event"] = event
        journal["post_ledger"] = ledger_receipt
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(JOURNAL, journal, uid=0, gid=0, mode=0o600)
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(RECOVERY_TRANSACTION, journal, uid=0, gid=0, mode=0o600)

        state_pre = gate["pre_state"]
        workflow_pre = gate["pre_workflow"]
        if not isinstance(state_pre, dict) or not isinstance(workflow_pre, dict):
            raise ValueError("recovery gate pre-state payloads are invalid")
        state_target = dict(state_pre)
        state_target["hard_stopped"] = False
        state_target["active_overlap_transaction"] = None
        state_target["last_event_utc"] = gate["recovery_utc"]
        state_target["recovered_from_source_prepare_py39_failure"] = recovery_id
        workflow_target = dict(workflow_pre)
        workflow_target["stage"] = "AUDIT_PASSED"
        workflow_target["hard_stopped"] = False
        workflow_target["active_transaction"] = None
        workflow_target["recovered_from_source_prepare_py39_failure"] = recovery_id
        state_pre_bytes = pretty_bytes(state_pre)
        state_target_bytes = pretty_bytes(state_target)
        workflow_pre_bytes = pretty_bytes(workflow_pre)
        workflow_target_bytes = pretty_bytes(workflow_target)
        current_state = STATE.read_bytes()
        if current_state == state_pre_bytes:
            verify_lock_binding(descriptor, contract, pre_runtime)
            atomic_bytes(STATE, state_target_bytes, uid=1000, gid=1000, mode=0o644)
        elif current_state != state_target_bytes:
            raise ValueError("budget state is neither authorized pre nor target bytes")
        state_receipt, observed_state = exact_receipt(
            STATE, uid=1000, gid=1000, mode=0o644
        )
        if observed_state != state_target_bytes:
            raise ValueError("budget state target receipt mismatch")
        if inherited_state is not None and state_receipt != inherited_state:
            raise ValueError("committed state receipt cannot be rebound")
        if inherited_state is not None:
            state_receipt = inherited_state
        journal = phase_record(base, "STATE_COMMITTED")
        journal["post_state"] = state_receipt
        journal["post_ledger"] = ledger_receipt
        journal["ledger_event"] = event
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(JOURNAL, journal, uid=0, gid=0, mode=0o600)
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(RECOVERY_TRANSACTION, journal, uid=0, gid=0, mode=0o600)

        current_workflow = WORKFLOW.read_bytes()
        if current_workflow == workflow_pre_bytes:
            verify_lock_binding(descriptor, contract, pre_runtime)
            atomic_bytes(WORKFLOW, workflow_target_bytes, uid=1000, gid=1000, mode=0o644)
        elif current_workflow != workflow_target_bytes:
            raise ValueError("workflow is neither authorized pre nor target bytes")
        workflow_receipt, observed_workflow = exact_receipt(
            WORKFLOW, uid=1000, gid=1000, mode=0o644
        )
        if observed_workflow != workflow_target_bytes:
            raise ValueError("workflow target receipt mismatch")
        if inherited_workflow is not None and workflow_receipt != inherited_workflow:
            raise ValueError("committed workflow receipt cannot be rebound")
        if inherited_workflow is not None:
            workflow_receipt = inherited_workflow
        journal = phase_record(base, "WORKFLOW_COMMITTED")
        journal.update({
            "post_state": state_receipt,
            "post_workflow": workflow_receipt,
            "post_ledger": ledger_receipt,
            "ledger_event": event,
        })
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(JOURNAL, journal, uid=0, gid=0, mode=0o600)
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(RECOVERY_TRANSACTION, journal, uid=0, gid=0, mode=0o600)
        terminal = phase_record(base, "SUCCESS_COMMITTED")
        terminal.update({
            "post_state": state_receipt,
            "post_workflow": workflow_receipt,
            "post_ledger": ledger_receipt,
            "ledger_event": event,
            "retired_inventory": retired_inventory,
        })
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(RECOVERY_TRANSACTION, terminal, uid=0, gid=0, mode=0o600)
        verify_lock_binding(descriptor, contract, pre_runtime)
        atomic_json(JOURNAL, terminal, uid=0, gid=0, mode=0o600)
        final_state, final_state_bytes = exact_receipt(STATE, uid=1000, gid=1000, mode=0o644)
        final_workflow, final_workflow_bytes = exact_receipt(WORKFLOW, uid=1000, gid=1000, mode=0o644)
        final_ledger, final_ledger_bytes = exact_receipt(LEDGER, uid=1000, gid=1000, mode=0o644)
        if (
            final_state != state_receipt
            or final_state_bytes != state_target_bytes
            or final_workflow != workflow_receipt
            or final_workflow_bytes != workflow_target_bytes
            or final_ledger != ledger_receipt
            or final_ledger_bytes != original_ledger + event_line
        ):
            raise ValueError("post-terminal runtime identity drift")
        verify_lock_binding(descriptor, contract, pre_runtime)
        print(json.dumps({"status": "source_prepare_py39_recovered", "recovery_id": recovery_id}, sort_keys=True))
        return 0
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def main() -> int:
    isolated_bootstrap()
    if len(sys.argv) != 2 or sys.argv[1] not in {"create-gate", "recover"}:
        raise SystemExit("usage: m9_source_prepare_py39_recovery.py {create-gate|recover}")
    return create_gate() if sys.argv[1] == "create-gate" else recover()


if __name__ == "__main__":
    raise SystemExit(main())
