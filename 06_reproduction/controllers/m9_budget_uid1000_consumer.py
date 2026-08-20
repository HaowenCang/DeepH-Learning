#!/usr/bin/env python3
"""Least-privilege D-018 adapter for exactly one UID1000 source_prepare.

The audited M9 controller and source-launcher control directory remain byte
identical to their post-migration freeze.  This adapter verifies a separate
root-issued consumer gate while the original controller holds budget.lock,
then supplies the sealed execution-fact receipt to the unchanged controller.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys


PROJECT_ROOT = Path("/mnt/e/Projects/Codex/DeepH")
REPRODUCTION = PROJECT_ROOT / "06_reproduction"
AUDITS = PROJECT_ROOT / "08_audits"
MANIFESTS = Path("/home/evan-williams/deeph-m9/manifests")
PROJECT_ADAPTER = REPRODUCTION / "controllers/m9_budget_uid1000_consumer.py"
PROJECT_ORIGINAL_CONTROLLER = REPRODUCTION / "scripts/m9_budget.py"
SNAPSHOT_ROOT = Path("/home/evan-williams/deeph-m9/controls/uid1000-consumer")
SNAPSHOT_MANIFEST = SNAPSHOT_ROOT / "snapshot_manifest.json"
INSTALLED_ADAPTER = SNAPSHOT_ROOT / "m9_budget_uid1000_consumer.py"
ORIGINAL_CONTROLLER = SNAPSHOT_ROOT / "m9_budget.py"
CONSUMER_WORK_PACKAGE = AUDITS / "M9_unlimited_wall_clock_uid1000_consumer_work_package.md"
CONSUMER_FROZEN_HASHES = (
    REPRODUCTION / "manifests/m9_unlimited_wall_clock_uid1000_consumer_frozen_hashes.json"
)
CONSUMER_VERDICT = AUDITS / "M9_unlimited_wall_clock_uid1000_consumer_final_verdict.json"
CONSUMER_REPORT = (
    AUDITS / "M9_unlimited_wall_clock_uid1000_consumer_third_targeted_reaudit.md"
)
CONSUMER_GATE = MANIFESTS / "overlap_unlimited_wall_clock_uid1000_consumer_gate.json"
EXECUTION_GATE = MANIFESTS / "overlap_unlimited_wall_clock_execution_gate.json"
AUTHORIZATION = AUDITS / "M9_unlimited_wall_clock_authorization.md"

CONSUMER_CONTROL_FILES = {
    PROJECT_ADAPTER,
    REPRODUCTION / "controllers/m9_uid1000_consumer_bootstrap.py",
    REPRODUCTION / "controllers/m9_uid1000_consumer_install.py",
    REPRODUCTION / "tests/test_m9_uid1000_consumer.py",
    REPRODUCTION / "manifests/m9_uid1000_consumer_contract.json",
    PROJECT_ORIGINAL_CONTROLLER,
    REPRODUCTION / "tests/test_m9_overlap_controls.py",
    REPRODUCTION / "configs/m9_overlap_only_contract.json",
    REPRODUCTION / "manifests/budget_contract.json",
    REPRODUCTION / "manifests/m9_overlap_frozen_hashes.json",
    REPRODUCTION / "manifests/m9_unlimited_wall_clock_contract.json",
    REPRODUCTION / "manifests/m9_unlimited_wall_clock_frozen_hashes.json",
    REPRODUCTION / "scripts/m9_overlap_common.py",
    REPRODUCTION / "scripts/m9_overlap_source_launcher.py",
    AUTHORIZATION,
    CONSUMER_WORK_PACKAGE,
    AUDITS / "M9_unlimited_wall_clock_execution_gate_fact_audit.md",
    AUDITS / "M9_unlimited_wall_clock_uid1000_consumer_targeted_reaudit.md",
    AUDITS / "M9_unlimited_wall_clock_uid1000_consumer_second_targeted_reaudit.md",
    AUDITS / "M9_unlimited_wall_clock_migration_execution_independent_audit.md",
    AUDITS / "M9_unlimited_wall_clock_migration_execution_final_verdict.json",
    PROJECT_ROOT / "decisions.md",
    PROJECT_ROOT / "00_scope/master_execution_plan.md",
    PROJECT_ROOT / "08_audits/progress_tracker.md",
}
CONSUMER_SNAPSHOT_SOURCES = CONSUMER_CONTROL_FILES | {
    CONSUMER_FROZEN_HASHES,
    CONSUMER_VERDICT,
    CONSUMER_REPORT,
}


def load_original_controller() -> object:
    specification = importlib.util.spec_from_file_location(
        "m9_budget_original_d018", ORIGINAL_CONTROLLER
    )
    if specification is None or specification.loader is None:
        raise SystemExit("cannot load the frozen M9 controller")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


_M9: object | None = None


def original_controller() -> object:
    global _M9
    if _M9 is None:
        _M9 = load_original_controller()
    return _M9


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_snapshot_regular(path: Path) -> tuple[dict[str, object], bytes]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != 0
            or before.st_gid != 1000
            or stat.S_IMODE(before.st_mode) != 0o440
            or before.st_nlink != 1
        ):
            raise SystemExit(f"consumer snapshot metadata mismatch: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        stable = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if any(getattr(before, key) != getattr(after, key) for key in stable):
            raise SystemExit(f"consumer snapshot changed during read: {path}")
        payload = b"".join(chunks)
        if len(payload) != after.st_size:
            raise SystemExit(f"consumer snapshot read was incomplete: {path}")
        receipt = {
            "path": path.as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "uid": after.st_uid,
            "gid": after.st_gid,
            "mode": stat.S_IMODE(after.st_mode),
            "nlink": after.st_nlink,
        }
        return receipt, payload
    finally:
        os.close(descriptor)


def read_snapshot_manifest() -> tuple[dict[str, object], dict[str, object]]:
    root_stat = os.lstat(SNAPSHOT_ROOT)
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or root_stat.st_uid != 0
        or root_stat.st_gid != 1000
        or stat.S_IMODE(root_stat.st_mode) != 0o550
    ):
        raise SystemExit("consumer snapshot root metadata mismatch")
    receipt, payload = read_snapshot_regular(SNAPSHOT_MANIFEST)
    value = json.loads(payload.decode("utf-8"))
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != "m9-uid1000-consumer-snapshot-v1"
        or not isinstance(value.get("files"), dict)
    ):
        raise SystemExit("consumer snapshot manifest schema mismatch")
    return receipt, value


def snapshot_source_payload(
    manifest: dict[str, object], source: Path
) -> tuple[dict[str, object], bytes]:
    files = manifest["files"]
    entry = files.get(source.as_posix())
    if not isinstance(entry, dict) or set(entry) != {
        "snapshot_path", "sha256", "bytes"
    }:
        raise SystemExit(f"consumer snapshot entry mismatch: {source}")
    snapshot_path = Path(str(entry["snapshot_path"]))
    if snapshot_path.parent != SNAPSHOT_ROOT:
        raise SystemExit("consumer snapshot member escaped its root")
    receipt, payload = read_snapshot_regular(snapshot_path)
    if (
        receipt["sha256"] != entry["sha256"]
        or receipt["bytes"] != int(entry["bytes"])
    ):
        raise SystemExit(f"consumer snapshot receipt mismatch: {source}")
    return receipt, payload


def consumer_runtime_snapshot() -> tuple[dict[str, object], dict[str, bytes]]:
    m9 = original_controller()
    paths = {
        "state_sha256": m9.STATE_PATH,
        "workflow_sha256": m9.OVERLAP_WORKFLOW_STATE,
        "ledger_sha256": m9.LEDGER_PATH,
        "overlap_transaction_sha256": m9.OVERLAP_TRANSACTION,
        "source_control_recovery_transaction_sha256":
            m9.SOURCE_CONTROL_RECOVERY_TRANSACTION,
        "d018_gate_sha256": m9.UNLIMITED_WALL_CLOCK_GATE,
        "d018_transaction_sha256": m9.UNLIMITED_WALL_CLOCK_TRANSACTION,
        "d018_execution_gate_sha256": EXECUTION_GATE,
        "active_overlap_gate_sha256": m9.OVERLAP_AUDIT_GATE,
    }
    expected_metadata = {
        "state_sha256": (1000, 1000, 0o644),
        "workflow_sha256": (1000, 1000, 0o644),
        "ledger_sha256": (1000, 1000, 0o644),
        "overlap_transaction_sha256": (1000, 1000, 0o644),
        "source_control_recovery_transaction_sha256": (1000, 1000, 0o644),
        "d018_gate_sha256": (0, 1000, 0o640),
        "d018_transaction_sha256": (0, 1000, 0o640),
        "d018_execution_gate_sha256": (0, 1000, 0o640),
        "active_overlap_gate_sha256": (0, 1000, 0o640),
    }
    observed: dict[str, object] = {}
    payloads: dict[str, bytes] = {}
    for key, path in paths.items():
        receipt, payload = m9.read_stable_regular_bytes(path)
        uid, gid, mode = expected_metadata[key]
        if (
            receipt.get("uid") != uid
            or receipt.get("gid") != gid
            or receipt.get("mode") != mode
            or receipt.get("nlink") != 1
        ):
            raise SystemExit(f"D-018 consumer runtime metadata mismatch: {path}")
        observed[key] = receipt
        payloads[key] = payload
    observed["source_products_present"] = [
        path.as_posix()
        for path in m9.SOURCE_RECOVERY_PRODUCTS
        if os.path.lexists(path)
    ]
    return observed, payloads


def consumer_runtime_receipts() -> dict[str, object]:
    receipts, _ = consumer_runtime_snapshot()
    return receipts


def verify_consumer_gate() -> dict[str, object]:
    m9 = original_controller()
    if not hasattr(os, "geteuid") or os.geteuid() != 1000:
        raise SystemExit("D-018 consumer adapter requires project UID 1000")
    gate_receipt, gate, _ = m9.read_d018_control_json(CONSUMER_GATE)
    required_gate_fields = {
        "schema_version", "decision_id", "status", "blocking", "non_blocking",
        "scope", "verdict_path", "verdict_sha256", "frozen_hashes_path",
        "frozen_hashes_sha256", "authorization_path", "authorization_sha256",
        "snapshot_manifest_path", "snapshot_manifest_sha256",
        "execution_gate_path", "execution_gate_sha256",
        "sealed_execution_runtime_sha256", "d018_transaction_sha256", "runtime",
    }
    if set(gate) != required_gate_fields:
        raise SystemExit("D-018 consumer gate field closure mismatch")
    if (
        gate.get("schema_version")
        != "m9-unlimited-wall-clock-uid1000-consumer-gate-v1"
        or gate.get("decision_id") != "D-018"
        or gate.get("status") != "PASS"
        or int(gate.get("blocking", -1)) != 0
        or int(gate.get("non_blocking", -1)) != 0
        or gate.get("scope") != "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018"
    ):
        raise SystemExit("D-018 consumer gate is not an exact zero-issue PASS")

    snapshot_receipt, snapshot = read_snapshot_manifest()
    snapshot_files = snapshot["files"]
    if (
        gate.get("snapshot_manifest_path") != SNAPSHOT_MANIFEST.as_posix()
        or gate.get("snapshot_manifest_sha256") != snapshot_receipt["sha256"]
        or {Path(str(path)).resolve(strict=False) for path in snapshot_files}
        != {path.resolve(strict=False) for path in CONSUMER_SNAPSHOT_SOURCES}
    ):
        raise SystemExit("D-018 consumer snapshot closure mismatch")
    verdict_snapshot, verdict_bytes = snapshot_source_payload(snapshot, CONSUMER_VERDICT)
    verdict = json.loads(verdict_bytes.decode("utf-8"))
    if (
        verdict.get("schema_version")
        != "m9-unlimited-wall-clock-uid1000-consumer-audit-verdict-v1"
        or verdict.get("decision_id") != "D-018"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or gate.get("verdict_path") != CONSUMER_VERDICT.as_posix()
        or gate.get("verdict_sha256") != verdict_snapshot["sha256"]
    ):
        raise SystemExit("D-018 consumer verdict binding mismatch")
    report = Path(str(verdict.get("report_path", ""))).resolve(strict=False)
    report_snapshot, report_bytes = snapshot_source_payload(snapshot, CONSUMER_REPORT)
    work_snapshot, work_bytes = snapshot_source_payload(snapshot, CONSUMER_WORK_PACKAGE)
    if (
        report != CONSUMER_REPORT.resolve(strict=False)
        or report_snapshot["sha256"] != verdict.get("report_sha256")
        or hashlib.sha256(report_bytes).hexdigest() != verdict.get("report_sha256")
        or verdict.get("work_package_path") != CONSUMER_WORK_PACKAGE.as_posix()
        or work_snapshot["sha256"] != verdict.get("work_package_sha256")
        or hashlib.sha256(work_bytes).hexdigest() != verdict.get("work_package_sha256")
    ):
        raise SystemExit("D-018 consumer audit binding mismatch")

    authorization_snapshot, _ = snapshot_source_payload(snapshot, AUTHORIZATION)
    authorization_sha256 = str(authorization_snapshot["sha256"])
    if (
        gate.get("authorization_path") != AUTHORIZATION.as_posix()
        or gate.get("authorization_sha256") != authorization_sha256
    ):
        raise SystemExit("D-018 consumer authorization binding mismatch")
    frozen_snapshot, frozen_bytes = snapshot_source_payload(
        snapshot, CONSUMER_FROZEN_HASHES
    )
    frozen = json.loads(frozen_bytes.decode("utf-8"))
    if (
        gate.get("frozen_hashes_path") != CONSUMER_FROZEN_HASHES.as_posix()
        or gate.get("frozen_hashes_sha256") != frozen_snapshot["sha256"]
        or frozen.get("schema_version")
        != "m9-unlimited-wall-clock-uid1000-consumer-frozen-hashes-v1"
    ):
        raise SystemExit("D-018 consumer frozen binding mismatch")
    files = frozen.get("files")
    if (
        not isinstance(files, dict)
        or {Path(str(path)).resolve(strict=False) for path in files}
        != {path.resolve(strict=False) for path in CONSUMER_CONTROL_FILES}
    ):
        raise SystemExit("D-018 consumer frozen file closure mismatch")
    for text_path, expected_sha256 in files.items():
        source = Path(str(text_path))
        member_receipt, member_bytes = snapshot_source_payload(snapshot, source)
        if (
            member_receipt["sha256"] != str(expected_sha256)
            or hashlib.sha256(member_bytes).hexdigest() != str(expected_sha256)
        ):
            raise SystemExit(f"D-018 consumer frozen member mismatch: {source}")

    execution_receipt, execution_gate, _ = m9.read_d018_control_json(EXECUTION_GATE)
    required_execution_runtime = {
        "state_sha256", "workflow_sha256", "ledger_sha256",
        "overlap_transaction_sha256",
        "source_control_recovery_transaction_sha256",
        "source_control_recovery_gate_sha256", "d018_gate_sha256",
        "d018_transaction_sha256", "d018_journal_sha256",
        "d018_pre_state_snapshot_sha256", "retired_overlap_gate_sha256",
        "active_overlap_gate_sha256", "source_products_present",
    }
    execution_runtime = execution_gate.get("runtime")
    if (
        gate.get("execution_gate_path") != EXECUTION_GATE.as_posix()
        or gate.get("execution_gate_sha256") != execution_receipt["sha256"]
        or execution_gate.get("schema_version")
        != "m9-unlimited-wall-clock-execution-gate-v1"
        or execution_gate.get("status") != "PASS"
        or int(execution_gate.get("blocking", -1)) != 0
        or int(execution_gate.get("non_blocking", -1)) != 0
        or execution_gate.get("scope")
        != "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018"
        or not isinstance(execution_runtime, dict)
        or set(execution_runtime) != required_execution_runtime
        or execution_runtime.get("source_products_present") != []
        or gate.get("sealed_execution_runtime_sha256")
        != canonical_hash(execution_runtime)
        or gate.get("d018_transaction_sha256")
        != execution_gate.get("d018_transaction_sha256")
    ):
        raise SystemExit("D-018 sealed execution-fact gate mismatch")

    runtime, runtime_payloads = consumer_runtime_snapshot()
    if gate.get("runtime") != runtime or runtime.get("source_products_present") != []:
        raise SystemExit("D-018 consumer runtime drift")
    for key, value in runtime.items():
        if (
            key in execution_runtime
            and isinstance(value, dict)
            and execution_runtime.get(key) != value.get("sha256")
        ):
            raise SystemExit("D-018 consumer runtime differs from execution audit")
    state = json.loads(runtime_payloads["state_sha256"].decode("utf-8"))
    workflow = json.loads(runtime_payloads["workflow_sha256"].decode("utf-8"))
    transaction = json.loads(runtime_payloads["d018_transaction_sha256"].decode("utf-8"))
    if (
        m9.wall_clock_policy_mode(state) != "UNLIMITED"
        or state.get("hard_stopped")
        or state.get("active_overlap_transaction") is not None
        or workflow.get("stage") != "AUDIT_PASSED"
        or workflow.get("hard_stopped")
        or workflow.get("active_transaction") is not None
        or transaction.get("schema_version")
        != "m9-unlimited-wall-clock-transaction-v1"
        or transaction.get("state") != "SUCCESS_COMMITTED"
        or runtime["d018_transaction_sha256"]["sha256"]
        != gate.get("d018_transaction_sha256")
    ):
        raise SystemExit("D-018 consumer terminal state mismatch")
    terminal_runtime, _ = consumer_runtime_snapshot()
    if terminal_runtime != runtime:
        raise SystemExit("D-018 consumer runtime changed during verification")
    return {
        "gate_receipt": gate_receipt,
        "gate": gate,
        "execution_gate": execution_gate,
        "execution_gate_receipt": execution_receipt,
    }


def require_source_prepare_argv(argv: list[str]) -> None:
    if not argv or argv[0] != "run":
        raise SystemExit("consumer adapter accepts only the run subcommand")
    if "--overlap-operation" not in argv or "--overlap-action" not in argv:
        raise SystemExit("consumer adapter requires the frozen overlap action API")
    action_index = argv.index("--overlap-action")
    if action_index + 1 >= len(argv) or argv[action_index + 1] != "source_prepare":
        raise SystemExit("consumer adapter authorizes only source_prepare")
    if "--" in argv:
        raise SystemExit("consumer adapter forbids free argv")


def main() -> int:
    try:
        installed_adapter = INSTALLED_ADAPTER.resolve(strict=True)
    except OSError as exc:
        raise SystemExit("D-018 consumer snapshot is not installed") from exc
    if Path(__file__).resolve(strict=True) != installed_adapter:
        raise SystemExit("D-018 consumer must run from the root-owned snapshot")
    m9 = original_controller()
    require_source_prepare_argv(sys.argv[1:])
    original_atomic_json = m9.atomic_json
    first_state_write = True

    def verified() -> dict[str, object]:
        return verify_consumer_gate()

    def execution_ready_proxy() -> dict[str, object]:
        return verified()

    def execution_fact_proxy() -> dict[str, object]:
        result = verified()
        return {"gate": result["execution_gate"]}

    def runtime_proxy() -> dict[str, object]:
        result = verified()
        return dict(result["execution_gate"]["runtime"])

    def guarded_atomic_json(path: Path, value: dict) -> None:
        nonlocal first_state_write
        if first_state_write:
            verified()
            first_state_write = False
        original_atomic_json(path, value)

    m9.verify_unlimited_wall_clock_execution_ready = execution_ready_proxy
    m9.verify_unlimited_wall_clock_execution_fact_gate = execution_fact_proxy
    m9.d018_execution_runtime_receipts = runtime_proxy
    m9.atomic_json = guarded_atomic_json
    return int(m9.main())


if __name__ == "__main__":
    raise SystemExit(main())
