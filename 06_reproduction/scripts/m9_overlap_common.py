#!/usr/bin/env python3
"""Shared invariants for the frozen M9 overlap-only workflow."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import datetime as dt
from typing import Iterator


CONTRACT_PATH = Path(
    "/mnt/e/Projects/Codex/DeepH/06_reproduction/configs/m9_overlap_only_contract.json"
)
FROZEN_HASHES_PATH = Path(
    "/mnt/e/Projects/Codex/DeepH/06_reproduction/manifests/m9_overlap_py39_recovery_frozen_hashes.json"
)
EXPECTED_CONTRACT_SHA256 = "a0e6d017f568e5caa7fe7a49939330c88263058066af14ce8809ef625b36abb0"
WORKFLOW_LOCK = Path("/home/evan-williams/deeph-m9/manifests/overlap_workflow.lock")
_BUDGET_CONTEXT: dict[str, object] | None = None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def write_utf8_lf(path: Path, text: str) -> None:
    """Write the exact UTF-8 bytes produced by an LF-normalized renderer."""
    if "\r" in text:
        raise ValueError("rendered text contains a non-LF line ending")
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def install_budget_context(value: dict[str, object]) -> None:
    global _BUDGET_CONTEXT
    if _BUDGET_CONTEXT is not None:
        raise RuntimeError("budget context can only be installed once")
    if (
        value.get("schema_version") != "m9-overlap-capability-v1"
        or value.get("state") != "CONSUMED"
        or int(value.get("child_pid", -1)) != os.getpid()
        or int(value.get("budget_pid", -1)) != os.getppid()
    ):
        raise RuntimeError("invalid consumed budget capability")
    capability_id = str(value.get("capability_id", ""))
    transaction_id = str(value.get("transaction_id", ""))
    if not all(len(item) == 32 and all(c in "0123456789abcdef" for c in item) for item in (capability_id, transaction_id)):
        raise RuntimeError("budget capability IDs are invalid")
    capability_path = WORKFLOW_LOCK.parent / "overlap_capabilities" / f"{capability_id}.consumed.json"
    transaction_path = WORKFLOW_LOCK.parent / "overlap_transaction.json"
    consumed = load_json(capability_path, "m9-overlap-capability-v1")
    transaction = load_json(transaction_path, "m9-overlap-transaction-v1")
    if consumed != value or transaction.get("transaction_id") != transaction_id or transaction.get(
        "state"
    ) != "RUNNING" or int(transaction.get("child_pid", -1)) != os.getpid():
        raise RuntimeError("budget capability is not bound to the running transaction")
    _BUDGET_CONTEXT = dict(value)


def require_budget_context(bucket: str, actions: tuple[str, ...]) -> dict[str, object]:
    context = _BUDGET_CONTEXT
    if context is None:
        raise RuntimeError("formal overlap mutation requires a consumed budget capability")
    if context.get("bucket") != bucket or context.get("action") not in actions:
        raise RuntimeError("budget capability bucket/action mismatch")
    forecast = context.get("forecast_bytes")
    if isinstance(forecast, bool) or not isinstance(forecast, int) or forecast < 0:
        raise RuntimeError("budget capability forecast is invalid")
    return context


def canonical_json_sha256(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def require_exact_path(actual: Path, expected: str, label: str) -> Path:
    resolved = actual.resolve(strict=False)
    frozen = Path(expected).resolve(strict=False)
    if resolved != frozen:
        raise ValueError(f"{label} path is not frozen: {resolved} != {frozen}")
    return resolved


def load_contract(path: Path = CONTRACT_PATH) -> tuple[dict[str, object], str]:
    require_exact_path(path, CONTRACT_PATH.as_posix(), "contract")
    actual_hash = file_sha256(path)
    if actual_hash != EXPECTED_CONTRACT_SHA256:
        raise ValueError(
            f"contract SHA-256 mismatch: {actual_hash} != {EXPECTED_CONTRACT_SHA256}"
        )
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != "m9-overlap-only-contract-v1":
        raise ValueError("unexpected overlap contract schema")
    runtime_paths = contract.get("runtime_paths")
    if not isinstance(runtime_paths, dict):
        raise ValueError("contract runtime_paths is not an object")
    if runtime_paths.get("project_contract") != CONTRACT_PATH.as_posix():
        raise ValueError("contract does not bind its own frozen path")
    return contract, actual_hash


def runtime_path(contract: dict[str, object], name: str) -> Path:
    paths = contract["runtime_paths"]
    if not isinstance(paths, dict) or not isinstance(paths.get(name), str):
        raise ValueError(f"missing runtime path: {name}")
    return Path(str(paths[name]))


def expected_structure_ids(contract: dict[str, object]) -> list[str]:
    scope = contract["scope"]
    if not isinstance(scope, dict) or not isinstance(scope.get("structure_ids"), dict):
        raise ValueError("invalid structure ID contract")
    rule = scope["structure_ids"]
    values = list(
        range(int(rule["start"]), int(rule["stop_inclusive"]) + 1, int(rule["step"]))
    )
    if len(values) != int(rule["count"]):
        raise ValueError("structure ID rule does not match frozen count")
    return [str(value) for value in values]


def atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def load_json(path: Path, expected_schema: str | None = None) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    if expected_schema is not None and value.get("schema_version") != expected_schema:
        raise ValueError(f"unexpected schema in {path}: {value.get('schema_version')}")
    return value


def verify_audit_gate(contract: dict[str, object]) -> dict[str, object]:
    gate_path = runtime_path(contract, "audit_gate")
    gate = load_json(gate_path, "m9-overlap-audit-gate-v1")
    if gate.get("status") != "PASS":
        raise ValueError("overlap work-package audit gate is not PASS")
    if int(gate.get("blocking", -1)) != 0 or int(gate.get("non_blocking", -1)) != 0:
        raise ValueError("overlap audit gate has remaining issues")
    for field in ("work_package_sha256", "audit_report_sha256", "frozen_hashes_sha256"):
        value = gate.get(field)
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"audit gate lacks a SHA-256 field: {field}")
    if file_sha256(FROZEN_HASHES_PATH) != gate["frozen_hashes_sha256"]:
        raise ValueError("audit gate/frozen-hashes binding mismatch")
    for path_field, hash_field in (
        ("work_package_path", "work_package_sha256"),
        ("audit_report_path", "audit_report_sha256"),
    ):
        path = Path(str(gate.get(path_field, "")))
        if not path.is_file() or file_sha256(path) != gate[hash_field]:
            raise ValueError(f"audit gate object binding mismatch: {path_field}")
    hashes = load_json(FROZEN_HASHES_PATH, "m9-overlap-frozen-hashes-v1")
    if hashes.get("contract_sha256") != EXPECTED_CONTRACT_SHA256:
        raise ValueError("frozen hash manifest does not bind the contract")
    return gate


def verify_frozen_project_files(contract: dict[str, object]) -> dict[str, object]:
    gate = verify_audit_gate(contract)
    manifest = load_json(FROZEN_HASHES_PATH, "m9-overlap-frozen-hashes-v1")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("frozen hash manifest lacks files")
    for text_path, expected in files.items():
        path = Path(str(text_path))
        if not path.is_file() or file_sha256(path) != expected:
            raise ValueError(f"frozen project file mismatch: {path}")
    return gate


class workflow_lock:
    """Exclusive lock for workflow state transitions."""

    def __enter__(self) -> "workflow_lock":
        WORKFLOW_LOCK.parent.mkdir(parents=True, exist_ok=True)
        self.handle = WORKFLOW_LOCK.open("a+")
        fcntl.flock(self.handle, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.handle.close()


def load_workflow_state(contract: dict[str, object]) -> dict[str, object]:
    return load_json(runtime_path(contract, "workflow_state"), "m9-overlap-workflow-state-v1")


def save_workflow_state(contract: dict[str, object], state: dict[str, object]) -> None:
    if state.get("schema_version") != "m9-overlap-workflow-state-v1":
        raise ValueError("refusing to save invalid workflow state schema")
    atomic_json(runtime_path(contract, "workflow_state"), state)


def hard_stop_workflow(contract: dict[str, object], reason: str) -> None:
    """Best-effort irreversible stop after any formal workflow failure."""
    try:
        with workflow_lock():
            state = load_workflow_state(contract)
            state["hard_stopped"] = True
            state["stage"] = "HARD_STOP"
            state["hard_stop_reason"] = reason
            state["hard_stop_utc"] = dt.datetime.now(dt.timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
            save_workflow_state(contract, state)
    except Exception:
        pass


def regular_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in controlled tree: {path}")
        if path.is_file():
            yield path


def tree_inventory(root: Path, relative_paths: list[str] | None = None) -> dict[str, object]:
    if relative_paths is None:
        paths = list(regular_files(root))
    else:
        paths = [root / relative for relative in relative_paths]
    inventory: dict[str, object] = {}
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"inventory member is missing/non-regular: {path}")
        relative = path.relative_to(root).as_posix()
        inventory[relative] = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
    return inventory
