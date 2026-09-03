#!/usr/bin/env python3
"""One-shot completion of the post-refresh UID1000 readiness gate."""

from __future__ import annotations

import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys


PROJECT_ROOT = Path("/mnt/e/Projects/Codex/DeepH")
AUDITS = PROJECT_ROOT / "08_audits"
PROJECT_CONTROLLER = (
    PROJECT_ROOT
    / "06_reproduction/controllers/m9_py39_consumer_gate_completion.py"
)
WORK_PACKAGE = AUDITS / "M9_py39_consumer_gate_completion_work_package.md"
FAILURE_RECORD = AUDITS / "M9_py39_consumer_gate_completion_failure_record.md"
AUDIT_REPORT = AUDITS / "M9_py39_consumer_gate_completion_independent_audit.md"
AUDIT_VERDICT = AUDITS / "M9_py39_consumer_gate_completion_final_verdict.json"
TEST_PATH = (
    PROJECT_ROOT
    / "06_reproduction/tests/test_m9_py39_consumer_gate_completion.py"
)
TRUSTED_INSTALLER = Path(
    "/home/evan-williams/deeph-m9/controls/uid1000-consumer-py39-v2-bootstrap/"
    "m9_uid1000_consumer_install.py"
)
FROZEN_PYTHON = Path(
    "/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9"
)


def stable_bytes(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit(f"completion source metadata mismatch: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        linked = os.lstat(path)
        fields = (
            "st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink",
            "st_size",
        )
        if (
            any(getattr(before, key) != getattr(after, key) for key in fields)
            or any(getattr(after, key) != getattr(linked, key) for key in fields)
            or stat.S_ISLNK(linked.st_mode)
        ):
            raise SystemExit(f"completion source changed during read: {path}")
        payload = b"".join(chunks)
        if len(payload) != after.st_size:
            raise SystemExit(f"completion source read was incomplete: {path}")
        return payload
    finally:
        os.close(descriptor)


def load_trusted_installer() -> object:
    specification = importlib.util.spec_from_file_location(
        "m9_py39_gate_completion_trusted_installer", TRUSTED_INSTALLER
    )
    if specification is None or specification.loader is None:
        raise SystemExit("cannot load trusted v2 installer")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def verify_audit_authority(
    controller_sha: str,
    verdict_sha: str,
    report_sha: str,
    work_sha: str,
    failure_sha: str,
    test_sha: str,
) -> None:
    controller_bytes = stable_bytes(PROJECT_CONTROLLER)
    verdict_bytes = stable_bytes(AUDIT_VERDICT)
    report_bytes = stable_bytes(AUDIT_REPORT)
    work_bytes = stable_bytes(WORK_PACKAGE)
    failure_bytes = stable_bytes(FAILURE_RECORD)
    test_bytes = stable_bytes(TEST_PATH)
    observed = {
        "controller": hashlib.sha256(controller_bytes).hexdigest(),
        "verdict": hashlib.sha256(verdict_bytes).hexdigest(),
        "report": hashlib.sha256(report_bytes).hexdigest(),
        "work": hashlib.sha256(work_bytes).hexdigest(),
        "failure": hashlib.sha256(failure_bytes).hexdigest(),
        "test": hashlib.sha256(test_bytes).hexdigest(),
    }
    if observed != {
        "controller": controller_sha,
        "verdict": verdict_sha,
        "report": report_sha,
        "work": work_sha,
        "failure": failure_sha,
        "test": test_sha,
    }:
        raise SystemExit("completion audit argument hash mismatch")
    verdict = json.loads(verdict_bytes.decode("utf-8"))
    required = {
        "schema_version", "decision_id", "verdict", "blocking", "non_blocking",
        "controller_path", "controller_sha256", "work_package_path",
        "work_package_sha256", "failure_record_path",
        "failure_record_sha256", "test_path", "test_sha256", "report_path",
        "report_sha256",
    }
    if (
        not isinstance(verdict, dict)
        or set(verdict) != required
        or verdict.get("schema_version")
        != "m9-py39-consumer-gate-completion-verdict-v1"
        or verdict.get("decision_id")
        != "D-018-PY39-CONSUMER-GATE-COMPLETION"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("controller_path") != PROJECT_CONTROLLER.as_posix()
        or verdict.get("controller_sha256") != controller_sha
        or verdict.get("work_package_path") != WORK_PACKAGE.as_posix()
        or verdict.get("work_package_sha256") != work_sha
        or verdict.get("failure_record_path") != FAILURE_RECORD.as_posix()
        or verdict.get("failure_record_sha256") != failure_sha
        or verdict.get("test_path") != TEST_PATH.as_posix()
        or verdict.get("test_sha256") != test_sha
        or verdict.get("report_path") != AUDIT_REPORT.as_posix()
        or verdict.get("report_sha256") != report_sha
    ):
        raise SystemExit("completion independent verdict binding mismatch")


def normalized_refresh_for_gate(
    refresh: dict[str, object], runtime: dict[str, object]
) -> dict[str, object]:
    active = refresh.get("active")
    runtime_active = runtime.get("active_overlap_gate_sha256")
    if not isinstance(active, dict) or not isinstance(runtime_active, dict):
        raise SystemExit("completion active receipt is not an object")
    if set(active) != set(runtime_active) | {"dev", "ino"}:
        raise SystemExit("completion active receipt field delta mismatch")
    if (
        type(active.get("dev")) is not int
        or int(active["dev"]) <= 0
        or type(active.get("ino")) is not int
        or int(active["ino"]) <= 0
        or {key: active[key] for key in runtime_active} != runtime_active
    ):
        raise SystemExit("completion active receipt shared-field mismatch")
    normalized = dict(refresh)
    normalized["active"] = dict(runtime_active)
    return normalized


def read_terminal_snapshot(
    installer: object, payloads: dict[Path, bytes]
) -> dict[str, object]:
    """Verify the already sealed snapshot without invoking its installer."""
    consumer = installer.consumer
    if (
        not os.path.lexists(consumer.SNAPSHOT_ROOT)
        or os.path.lexists(installer.STAGING_ROOT)
    ):
        raise SystemExit("completion requires the sealed snapshot terminal namespace")
    receipt, manifest = consumer.read_snapshot_manifest()
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != {
        path.as_posix() for path in payloads
    }:
        raise SystemExit("completion snapshot source closure mismatch")
    expected_names = {consumer.SNAPSHOT_MANIFEST.name}
    for source, expected_payload in payloads.items():
        entry = files.get(source.as_posix())
        if not isinstance(entry, dict):
            raise SystemExit("completion snapshot entry is not an object")
        member = Path(str(entry.get("snapshot_path")))
        if member.parent != consumer.SNAPSHOT_ROOT:
            raise SystemExit("completion snapshot member escaped its root")
        expected_names.add(member.name)
        _, observed_payload = consumer.snapshot_source_payload(manifest, source)
        if observed_payload != expected_payload:
            raise SystemExit("completion snapshot member bytes mismatch")
    if {path.name for path in consumer.SNAPSHOT_ROOT.iterdir()} != expected_names:
        raise SystemExit("completion snapshot directory is not closed")
    return {"receipt": receipt, "manifest": manifest}


def read_terminal_refresh(
    installer: object,
    snapshot: dict[str, object],
    lock_handle: object,
) -> tuple[dict[str, object], dict[str, object]]:
    """Prove SUCCESS_COMMITTED and its namespace using read-only helpers."""
    core = installer.verify_recovered_core(lock_handle)
    journal, new_sha = installer.read_bound_refresh_journal(
        snapshot, lock_handle, core
    )
    if journal is None or journal.get("state") != "SUCCESS_COMMITTED":
        raise SystemExit("completion requires a SUCCESS_COMMITTED refresh journal")
    observed = installer.validate_refresh_namespace(journal, new_sha)
    refresh = {
        "active": observed["active"],
        "retired": observed["retired"],
        "journal": journal,
    }
    installer.verify_installation_preflight(
        lock_handle, expected=core, snapshot=snapshot, refresh=refresh
    )
    return core, refresh


def filesystem_receipt(path: Path) -> dict[str, object]:
    """Capture a stable no-follow receipt for one formal namespace member."""
    before = os.lstat(path)
    common: dict[str, object] = {
        "path": path.as_posix(),
        "dev": before.st_dev,
        "ino": before.st_ino,
        "uid": before.st_uid,
        "gid": before.st_gid,
        "mode": stat.S_IMODE(before.st_mode),
        "nlink": before.st_nlink,
        "bytes": before.st_size,
        "mtime_ns": before.st_mtime_ns,
        "ctime_ns": before.st_ctime_ns,
    }
    if stat.S_ISREG(before.st_mode):
        payload = stable_bytes(path)
        after = os.lstat(path)
        if (
            before.st_dev != after.st_dev
            or before.st_ino != after.st_ino
            or before.st_mode != after.st_mode
            or before.st_uid != after.st_uid
            or before.st_gid != after.st_gid
            or before.st_nlink != after.st_nlink
            or before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or before.st_ctime_ns != after.st_ctime_ns
        ):
            raise SystemExit(f"completion formal file drift: {path}")
        return common | {
            "kind": "file",
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    if stat.S_ISDIR(before.st_mode):
        return common | {"kind": "directory"}
    if stat.S_ISLNK(before.st_mode):
        target = os.readlink(path)
        after = os.lstat(path)
        if (
            before.st_dev != after.st_dev
            or before.st_ino != after.st_ino
            or before.st_mode != after.st_mode
            or before.st_uid != after.st_uid
            or before.st_gid != after.st_gid
            or before.st_nlink != after.st_nlink
            or before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or before.st_ctime_ns != after.st_ctime_ns
            or target != os.readlink(path)
        ):
            raise SystemExit(f"completion formal symlink drift: {path}")
        return common | {"kind": "symlink", "target": target}
    raise SystemExit(f"completion formal namespace has a special file: {path}")


def capture_tree(root: Path) -> dict[str, dict[str, object]]:
    """Capture a closed recursive tree without following links."""
    if not os.path.lexists(root):
        raise SystemExit(f"completion formal root is missing: {root}")
    result: dict[str, dict[str, object]] = {}

    def visit(path: Path) -> None:
        receipt = filesystem_receipt(path)
        result[path.as_posix()] = receipt
        if receipt["kind"] != "directory":
            return
        before_names = sorted(child.name for child in path.iterdir())
        for name in before_names:
            visit(path / name)
        after_names = sorted(child.name for child in path.iterdir())
        after = filesystem_receipt(path)
        if before_names != after_names or after != receipt:
            raise SystemExit(f"completion formal directory drift: {path}")

    visit(root)
    return result


def capture_formal_namespace_once(
    installer: object,
) -> dict[str, dict[str, object]]:
    roots = {
        installer.consumer.MANIFESTS,
        installer.consumer.SNAPSHOT_ROOT.parent,
        installer.REFRESH_JOURNAL.parent,
    }
    captured: dict[str, dict[str, object]] = {}
    for root in sorted(roots, key=lambda item: item.as_posix()):
        tree = capture_tree(root)
        overlap = set(captured) & set(tree)
        if overlap:
            raise SystemExit("completion formal roots overlap")
        captured.update(tree)
    return captured


def capture_formal_namespace(installer: object) -> dict[str, dict[str, object]]:
    """Require two equal closed-tree passes before accepting a formal snapshot."""
    first = capture_formal_namespace_once(installer)
    second = capture_formal_namespace_once(installer)
    if first != second:
        raise SystemExit("completion formal namespace drift between full passes")
    return second


def immutable_directory_receipt(receipt: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in receipt.items()
        if key not in {"bytes", "mtime_ns", "ctime_ns"}
    }


def verify_completion_write_set(
    before: dict[str, dict[str, object]],
    after: dict[str, dict[str, object]],
    gate_path: Path,
    gate_receipt: dict[str, object],
    existed_before: bool,
) -> None:
    """Allow only first creation of the gate, or an exact read-only replay."""
    if existed_before:
        if before != after:
            raise SystemExit("existing consumer gate replay changed formal state")
        return
    gate_key = gate_path.as_posix()
    parent_key = gate_path.parent.as_posix()
    if gate_key in before or gate_key not in after:
        raise SystemExit("consumer gate creation state mismatch")
    changed = {
        key for key in set(before) | set(after) if before.get(key) != after.get(key)
    }
    if not changed <= {gate_key, parent_key} or gate_key not in changed:
        raise SystemExit("completion changed an object outside the consumer gate")
    if parent_key not in before or parent_key not in after:
        raise SystemExit("consumer gate parent receipt is missing")
    if immutable_directory_receipt(before[parent_key]) != immutable_directory_receipt(
        after[parent_key]
    ):
        raise SystemExit("consumer gate parent security identity changed")
    installed = after[gate_key]
    if installed.get("kind") != "file" or any(
        installed.get(key) != gate_receipt.get(key)
        for key in ("path", "bytes", "sha256", "uid", "gid", "mode", "nlink")
    ):
        raise SystemExit("installed consumer gate receipt mismatch")


def run_completion_under_lock(
    installer: object,
    payloads: dict[Path, bytes],
    historical: dict[str, object],
    lock_handle: object,
    action: str,
) -> dict[str, object]:
    """Run after a terminal-only, zero-write gate under the existing lock."""
    if action not in {"preflight", "complete"}:
        raise SystemExit("completion action must be preflight or complete")
    installer.verify_installation_guard(historical, "before completion terminal gate")
    snapshot = read_terminal_snapshot(installer, payloads)
    terminal_core, terminal_refresh = read_terminal_refresh(
        installer, snapshot, lock_handle
    )
    gate_exists = os.path.lexists(installer.consumer.CONSUMER_GATE)
    if action == "preflight" and gate_exists:
        raise SystemExit("completion preflight requires the consumer gate to be absent")
    before = capture_formal_namespace(installer)

    replay_core, replay_snapshot = installer.prepare_snapshot_for_refresh(
        payloads, lock_handle
    )
    replay_refresh = installer.refresh_active_overlap_gate(
        replay_snapshot, lock_handle
    )
    if (
        replay_core != terminal_core
        or replay_snapshot != snapshot
        or replay_refresh != terminal_refresh
    ):
        raise SystemExit("completion terminal replay receipt drift")
    installer.verify_installation_preflight(
        lock_handle,
        expected=terminal_core,
        snapshot=snapshot,
        refresh=terminal_refresh,
    )
    runtime = installer.consumer.consumer_runtime_receipts()
    normalized = normalized_refresh_for_gate(terminal_refresh, runtime)
    gate = installer.build_consumer_gate(snapshot, normalized, historical)
    installer.verify_installation_guard(historical, "after completion gate build")
    installer.verify_installation_preflight(
        lock_handle,
        expected=terminal_core,
        snapshot=snapshot,
        refresh=terminal_refresh,
    )
    replayed = capture_formal_namespace(installer)
    if replayed != before:
        raise SystemExit("completion terminal replay was not zero-write")
    gate_payload = (json.dumps(gate, ensure_ascii=False, indent=2) + "\n").encode()
    if action == "preflight":
        return {
            "status": "preflight_pass",
            "gate_sha256": hashlib.sha256(gate_payload).hexdigest(),
        }

    receipt = installer.install_consumer_gate(gate)
    installer.verify_installation_preflight(
        lock_handle,
        expected=terminal_core,
        snapshot=snapshot,
        refresh=terminal_refresh,
    )
    installer.verify_installation_guard(
        historical, "after completion gate installation"
    )
    completed = capture_formal_namespace(installer)
    verify_completion_write_set(
        before,
        completed,
        installer.consumer.CONSUMER_GATE,
        receipt,
        gate_exists,
    )
    return {"status": "consumer_gate_completed", "receipt": receipt}


def run_completion(action: str) -> dict[str, object]:
    installer = load_trusted_installer()
    frozen_payload = installer.stable_source_bytes(
        installer.consumer.CONSUMER_FROZEN_HASHES
    )
    frozen_sha, verdict_bytes, report_bytes = installer.verify_trusted_bootstrap(
        frozen_payload
    )
    payloads = installer.verify_authorized_sources(
        frozen_sha, verdict_bytes, report_bytes
    )
    installer.consumer._M9 = installer.load_frozen_original_controller(
        payloads[installer.consumer.PROJECT_ORIGINAL_CONTROLLER]
    )
    historical = installer.consumer.verify_historical_consumer_evidence()
    m9 = installer.consumer.original_controller()
    lock_flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    lock_descriptor = os.open(m9.LOCK_PATH, lock_flags)
    with os.fdopen(lock_descriptor, "r+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        return run_completion_under_lock(
            installer, payloads, historical, lock_handle, action
        )


def main() -> int:
    if (
        not hasattr(os, "geteuid")
        or os.geteuid() != 0
        or Path(sys.executable).resolve(strict=True) != FROZEN_PYTHON.resolve(strict=True)
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
        or len(sys.argv) != 8
    ):
        raise SystemExit("completion requires root frozen Python -I -S -B and seven arguments")
    (
        controller_sha,
        action,
        verdict_sha,
        report_sha,
        work_sha,
        failure_sha,
        test_sha,
    ) = sys.argv[1:]
    if action not in {"preflight", "complete"}:
        raise SystemExit("completion action must be preflight or complete")
    verify_audit_authority(
        controller_sha,
        verdict_sha,
        report_sha,
        work_sha,
        failure_sha,
        test_sha,
    )
    result = run_completion(action)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
