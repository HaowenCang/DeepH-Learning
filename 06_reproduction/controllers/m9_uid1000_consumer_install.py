#!/usr/bin/env python3
"""Root-only durable installer for the audited UID1000 consumer snapshot/gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys


PROJECT_ADAPTER = Path(
    "/mnt/e/Projects/Codex/DeepH/06_reproduction/controllers/"
    "m9_budget_uid1000_consumer.py"
)
TRUSTED_BOOTSTRAP_ROOT = Path(
    "/home/evan-williams/deeph-m9/controls/uid1000-consumer-bootstrap"
)
TRUSTED_INSTALLER = TRUSTED_BOOTSTRAP_ROOT / "m9_uid1000_consumer_install.py"
TRUSTED_ADAPTER = TRUSTED_BOOTSTRAP_ROOT / "m9_budget_uid1000_consumer.py"
TRUSTED_BOOTSTRAP = TRUSTED_BOOTSTRAP_ROOT / "m9_uid1000_consumer_bootstrap.py"
TRUSTED_VERDICT = (
    TRUSTED_BOOTSTRAP_ROOT / "M9_unlimited_wall_clock_uid1000_consumer_final_verdict.json"
)
TRUSTED_REPORT = (
    TRUSTED_BOOTSTRAP_ROOT
    / "M9_unlimited_wall_clock_uid1000_consumer_third_targeted_reaudit.md"
)
TRUSTED_RECEIPT = TRUSTED_BOOTSTRAP_ROOT / "bootstrap_receipt.json"
RUNNING_INSTALLER = Path(__file__).resolve(strict=True)
if (
    __name__ == "__main__"
    and RUNNING_INSTALLER != TRUSTED_INSTALLER.resolve(strict=False)
):
    raise SystemExit("consumer installer must run from the trusted bootstrap")
ADAPTER_IMPORT = (
    TRUSTED_ADAPTER
    if RUNNING_INSTALLER == TRUSTED_INSTALLER.resolve(strict=False)
    else PROJECT_ADAPTER
)
specification = importlib.util.spec_from_file_location("m9_uid1000_consumer", ADAPTER_IMPORT)
if specification is None or specification.loader is None:
    raise RuntimeError("cannot load consumer adapter")
consumer = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = consumer
specification.loader.exec_module(consumer)


STAGING_ROOT = consumer.SNAPSHOT_ROOT.with_name(consumer.SNAPSHOT_ROOT.name + ".staging")
FROZEN_PYTHON = Path("/home/evan-williams/deeph-m9/env/deeph-v022/bin/python3.9")


def verify_trusted_bootstrap(frozen_payload: bytes) -> tuple[str, bytes, bytes]:
    root_stat = os.lstat(TRUSTED_BOOTSTRAP_ROOT)
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or root_stat.st_uid != 0
        or root_stat.st_gid != 1000
        or stat.S_IMODE(root_stat.st_mode) != 0o550
    ):
        raise SystemExit("trusted consumer bootstrap root metadata mismatch")
    members = {
        TRUSTED_BOOTSTRAP, TRUSTED_INSTALLER, TRUSTED_ADAPTER,
        TRUSTED_VERDICT, TRUSTED_REPORT, TRUSTED_RECEIPT,
    }
    if set(TRUSTED_BOOTSTRAP_ROOT.iterdir()) != members:
        raise SystemExit("trusted consumer bootstrap directory is not closed")
    frozen_sha = hashlib.sha256(frozen_payload).hexdigest()
    frozen = json.loads(frozen_payload.decode("utf-8"))
    files = frozen.get("files")
    source_mapping = {
        TRUSTED_BOOTSTRAP: consumer.REPRODUCTION / "controllers/m9_uid1000_consumer_bootstrap.py",
        TRUSTED_INSTALLER: consumer.REPRODUCTION / "controllers/m9_uid1000_consumer_install.py",
        TRUSTED_ADAPTER: consumer.PROJECT_ADAPTER,
        TRUSTED_VERDICT: consumer.CONSUMER_VERDICT,
        TRUSTED_REPORT: consumer.CONSUMER_REPORT,
    }
    expected_members: dict[str, object] = {}
    trusted_payloads: dict[Path, bytes] = {}
    for trusted, source in source_mapping.items():
        payload = stable_source_bytes(trusted)
        trusted_payloads[trusted] = payload
        observed = os.lstat(trusted)
        expected_sha = (
            files.get(source.as_posix())
            if isinstance(files, dict) and trusted not in {TRUSTED_VERDICT, TRUSTED_REPORT}
            else hashlib.sha256(payload).hexdigest()
        )
        if (
            observed.st_uid != 0
            or observed.st_gid != 1000
            or stat.S_IMODE(observed.st_mode) != 0o440
            or observed.st_nlink != 1
            or hashlib.sha256(payload).hexdigest() != expected_sha
        ):
            raise SystemExit(f"trusted consumer bootstrap member mismatch: {trusted}")
        expected_members[trusted.as_posix()] = {
            "sha256": expected_sha, "bytes": len(payload)
        }
    receipt_payload = stable_source_bytes(TRUSTED_RECEIPT)
    receipt_stat = os.lstat(TRUSTED_RECEIPT)
    receipt = json.loads(receipt_payload.decode("utf-8"))
    if (
        receipt_stat.st_uid != 0
        or receipt_stat.st_gid != 1000
        or stat.S_IMODE(receipt_stat.st_mode) != 0o440
        or receipt_stat.st_nlink != 1
        or receipt
        != {
            "schema_version": "m9-uid1000-consumer-bootstrap-v1",
            "decision_id": "D-018",
            "frozen_hashes_sha256": frozen_sha,
            "members": expected_members,
        }
    ):
        raise SystemExit("trusted consumer bootstrap receipt mismatch")
    return frozen_sha, trusted_payloads[TRUSTED_VERDICT], trusted_payloads[TRUSTED_REPORT]


def stable_source_bytes(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit(f"consumer source is not a single-link regular file: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        stable = ("st_dev", "st_ino", "st_mode", "st_uid", "st_gid", "st_nlink", "st_size")
        if any(getattr(before, key) != getattr(after, key) for key in stable):
            raise SystemExit(f"consumer source changed during read: {path}")
        payload = b"".join(chunks)
        if len(payload) != after.st_size:
            raise SystemExit(f"consumer source read was incomplete: {path}")
        return payload
    finally:
        os.close(descriptor)


def snapshot_name(source: Path, index: int) -> str:
    if source == consumer.PROJECT_ADAPTER:
        return "m9_budget_uid1000_consumer.py"
    if source == consumer.PROJECT_ORIGINAL_CONTROLLER:
        return "m9_budget.py"
    return f"{index:02d}-{source.name}"


def durable_snapshot_file(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o440)
    except FileExistsError:
        receipt, existing = consumer.read_snapshot_regular(path)
        if existing != payload or receipt["sha256"] != hashlib.sha256(payload).hexdigest():
            raise SystemExit(f"consumer staging member differs: {path}")
        return
    try:
        os.fchown(descriptor, 0, 1000)
        os.fchmod(descriptor, 0o440)
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("consumer snapshot write was short")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def verify_authorized_sources(
    expected_frozen_sha256: str,
    trusted_verdict_bytes: bytes,
    trusted_report_bytes: bytes,
) -> dict[Path, bytes]:
    frozen_bytes = stable_source_bytes(consumer.CONSUMER_FROZEN_HASHES)
    if hashlib.sha256(frozen_bytes).hexdigest() != expected_frozen_sha256:
        raise SystemExit("consumer frozen manifest differs from trusted bootstrap")
    frozen = json.loads(frozen_bytes.decode("utf-8"))
    files = frozen.get("files")
    if (
        frozen.get("schema_version")
        != "m9-unlimited-wall-clock-uid1000-consumer-frozen-hashes-v1"
        or not isinstance(files, dict)
        or {Path(str(path)).resolve(strict=False) for path in files}
        != {path.resolve(strict=False) for path in consumer.CONSUMER_CONTROL_FILES}
    ):
        raise SystemExit("consumer audit frozen closure mismatch")
    payloads: dict[Path, bytes] = {}
    for source in consumer.CONSUMER_CONTROL_FILES:
        payload = stable_source_bytes(source)
        if hashlib.sha256(payload).hexdigest() != files[source.as_posix()]:
            raise SystemExit(f"consumer audit source hash mismatch: {source}")
        payloads[source] = payload
    payloads[consumer.CONSUMER_FROZEN_HASHES] = frozen_bytes

    verdict_bytes = trusted_verdict_bytes
    verdict = json.loads(verdict_bytes.decode("utf-8"))
    report_bytes = trusted_report_bytes
    work_bytes = payloads[consumer.CONSUMER_WORK_PACKAGE]
    if (
        verdict.get("schema_version")
        != "m9-unlimited-wall-clock-uid1000-consumer-audit-verdict-v1"
        or verdict.get("decision_id") != "D-018"
        or verdict.get("verdict") != "PASS"
        or int(verdict.get("blocking", -1)) != 0
        or int(verdict.get("non_blocking", -1)) != 0
        or verdict.get("report_path") != consumer.CONSUMER_REPORT.as_posix()
        or verdict.get("report_sha256") != hashlib.sha256(report_bytes).hexdigest()
        or verdict.get("work_package_path") != consumer.CONSUMER_WORK_PACKAGE.as_posix()
        or verdict.get("work_package_sha256") != hashlib.sha256(work_bytes).hexdigest()
    ):
        raise SystemExit("consumer independent verdict binding mismatch")
    payloads[consumer.CONSUMER_VERDICT] = verdict_bytes
    payloads[consumer.CONSUMER_REPORT] = report_bytes
    return payloads


def verify_sealed_staging(payloads: dict[Path, bytes]) -> dict[str, object]:
    root_stat = os.lstat(STAGING_ROOT)
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or root_stat.st_uid != 0
        or root_stat.st_gid != 1000
        or stat.S_IMODE(root_stat.st_mode) != 0o550
    ):
        raise SystemExit("sealed consumer staging metadata mismatch")
    manifest_path = STAGING_ROOT / consumer.SNAPSHOT_MANIFEST.name
    manifest_payload = stable_source_bytes(manifest_path)
    manifest_stat = os.lstat(manifest_path)
    if (
        manifest_stat.st_uid != 0
        or manifest_stat.st_gid != 1000
        or stat.S_IMODE(manifest_stat.st_mode) != 0o440
        or manifest_stat.st_nlink != 1
    ):
        raise SystemExit("sealed consumer staging manifest metadata mismatch")
    manifest = json.loads(manifest_payload.decode("utf-8"))
    files = manifest.get("files")
    if (
        manifest.get("schema_version") != "m9-uid1000-consumer-snapshot-v1"
        or not isinstance(files, dict)
        or set(files) != {path.as_posix() for path in payloads}
    ):
        raise SystemExit("sealed consumer staging manifest closure mismatch")
    expected_names = {manifest_path.name}
    for source, payload in payloads.items():
        entry = files.get(source.as_posix())
        if not isinstance(entry, dict) or set(entry) != {
            "snapshot_path", "sha256", "bytes"
        }:
            raise SystemExit("sealed consumer staging entry mismatch")
        target = Path(str(entry["snapshot_path"]))
        if target.parent != consumer.SNAPSHOT_ROOT:
            raise SystemExit("sealed consumer staging target escaped final root")
        staged = STAGING_ROOT / target.name
        observed = stable_source_bytes(staged)
        staged_stat = os.lstat(staged)
        if (
            staged_stat.st_uid != 0
            or staged_stat.st_gid != 1000
            or stat.S_IMODE(staged_stat.st_mode) != 0o440
            or staged_stat.st_nlink != 1
            or observed != payload
            or entry["sha256"] != hashlib.sha256(payload).hexdigest()
            or int(entry["bytes"]) != len(payload)
        ):
            raise SystemExit("sealed consumer staging member mismatch")
        expected_names.add(staged.name)
    if {path.name for path in STAGING_ROOT.iterdir()} != expected_names:
        raise SystemExit("sealed consumer staging directory is not closed")
    return manifest


def install_snapshot(payloads: dict[Path, bytes]) -> dict[str, object]:
    parent = consumer.SNAPSHOT_ROOT.parent
    if not parent.exists():
        parent.mkdir(parents=True, mode=0o750)
        os.chown(parent, 0, 1000)
        os.chmod(parent, 0o750)
    parent_stat = os.lstat(parent)
    if (
        parent_stat.st_uid != 0
        or parent_stat.st_gid != 1000
        or stat.S_IMODE(parent_stat.st_mode) != 0o750
    ):
        raise SystemExit("consumer control parent metadata mismatch")
    if os.path.lexists(consumer.SNAPSHOT_ROOT):
        receipt, manifest = consumer.read_snapshot_manifest()
        if set(manifest["files"]) != {path.as_posix() for path in payloads}:
            raise SystemExit("installed consumer snapshot closure mismatch")
        expected_names = {
            Path(str(entry["snapshot_path"])).name
            for entry in manifest["files"].values()
        } | {consumer.SNAPSHOT_MANIFEST.name}
        if {path.name for path in consumer.SNAPSHOT_ROOT.iterdir()} != expected_names:
            raise SystemExit("installed consumer snapshot directory is not closed")
        for source, payload in payloads.items():
            _, observed = consumer.snapshot_source_payload(manifest, source)
            if observed != payload:
                raise SystemExit("installed consumer snapshot source mismatch")
        return {"receipt": receipt, "manifest": manifest}

    if not os.path.lexists(STAGING_ROOT):
        STAGING_ROOT.mkdir(mode=0o700)
        os.chown(STAGING_ROOT, 0, 1000)
        os.chmod(STAGING_ROOT, 0o700)
    staging_stat = os.lstat(STAGING_ROOT)
    if (
        stat.S_ISDIR(staging_stat.st_mode)
        and staging_stat.st_uid == 0
        and staging_stat.st_gid == 1000
        and stat.S_IMODE(staging_stat.st_mode) == 0o550
    ):
        verify_sealed_staging(payloads)
        os.replace(STAGING_ROOT, consumer.SNAPSHOT_ROOT)
        parent_descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
        receipt, installed = consumer.read_snapshot_manifest()
        return {"receipt": receipt, "manifest": installed}
    if (
        staging_stat.st_uid != 0
        or staging_stat.st_gid != 1000
        or stat.S_IMODE(staging_stat.st_mode) != 0o700
    ):
        raise SystemExit("consumer staging root metadata mismatch")
    entries: dict[str, object] = {}
    expected_staging_names = {consumer.SNAPSHOT_MANIFEST.name}
    for index, source in enumerate(sorted(payloads, key=lambda path: path.as_posix())):
        target = STAGING_ROOT / snapshot_name(source, index)
        if target.name in expected_staging_names:
            raise SystemExit("consumer snapshot target collision")
        expected_staging_names.add(target.name)
        durable_snapshot_file(target, payloads[source])
        entries[source.as_posix()] = {
            "snapshot_path": (consumer.SNAPSHOT_ROOT / target.name).as_posix(),
            "sha256": hashlib.sha256(payloads[source]).hexdigest(),
            "bytes": len(payloads[source]),
        }
    manifest = {
        "schema_version": "m9-uid1000-consumer-snapshot-v1",
        "decision_id": "D-018",
        "issue_id": "D018-EGF-B01",
        "files": entries,
    }
    manifest_payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    durable_snapshot_file(STAGING_ROOT / consumer.SNAPSHOT_MANIFEST.name, manifest_payload)
    if {path.name for path in STAGING_ROOT.iterdir()} != expected_staging_names:
        raise SystemExit("consumer staging directory is not closed")
    os.chmod(STAGING_ROOT, 0o550)
    directory = os.open(STAGING_ROOT, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    os.replace(STAGING_ROOT, consumer.SNAPSHOT_ROOT)
    parent_descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(parent_descriptor)
    finally:
        os.close(parent_descriptor)
    receipt, installed = consumer.read_snapshot_manifest()
    return {"receipt": receipt, "manifest": installed}


def build_consumer_gate(snapshot: dict[str, object]) -> dict[str, object]:
    m9 = consumer.original_controller()
    execution_receipt, execution_gate, _ = m9.read_d018_control_json(consumer.EXECUTION_GATE)
    runtime = consumer.consumer_runtime_receipts()
    verdict_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.CONSUMER_VERDICT
    )
    frozen_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.CONSUMER_FROZEN_HASHES
    )
    authorization_receipt, _ = consumer.snapshot_source_payload(
        snapshot["manifest"], consumer.AUTHORIZATION
    )
    return {
        "schema_version": "m9-unlimited-wall-clock-uid1000-consumer-gate-v1",
        "decision_id": "D-018",
        "status": "PASS",
        "blocking": 0,
        "non_blocking": 0,
        "scope": "ALLOW_ONE_D017_SOURCE_PREPARE_AFTER_D018",
        "verdict_path": consumer.CONSUMER_VERDICT.as_posix(),
        "verdict_sha256": verdict_receipt["sha256"],
        "frozen_hashes_path": consumer.CONSUMER_FROZEN_HASHES.as_posix(),
        "frozen_hashes_sha256": frozen_receipt["sha256"],
        "authorization_path": consumer.AUTHORIZATION.as_posix(),
        "authorization_sha256": authorization_receipt["sha256"],
        "snapshot_manifest_path": consumer.SNAPSHOT_MANIFEST.as_posix(),
        "snapshot_manifest_sha256": snapshot["receipt"]["sha256"],
        "execution_gate_path": consumer.EXECUTION_GATE.as_posix(),
        "execution_gate_sha256": execution_receipt["sha256"],
        "sealed_execution_runtime_sha256": consumer.canonical_hash(
            execution_gate["runtime"]
        ),
        "d018_transaction_sha256": execution_gate["d018_transaction_sha256"],
        "runtime": runtime,
    }


def main() -> int:
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise SystemExit("consumer snapshot installation requires root")
    if (
        Path(sys.executable).resolve(strict=True) != FROZEN_PYTHON.resolve(strict=True)
        or not sys.flags.isolated
        or not sys.flags.no_site
        or not sys.flags.dont_write_bytecode
    ):
        raise SystemExit("consumer snapshot installation requires frozen Python -I -S -B")
    try:
        trusted_installer = TRUSTED_INSTALLER.resolve(strict=True)
    except OSError as exc:
        raise SystemExit("trusted consumer bootstrap is not installed") from exc
    if RUNNING_INSTALLER != trusted_installer:
        raise SystemExit("consumer installer must run from the trusted bootstrap")
    frozen_payload = stable_source_bytes(consumer.CONSUMER_FROZEN_HASHES)
    frozen_sha256, verdict_bytes, report_bytes = verify_trusted_bootstrap(frozen_payload)
    payloads = verify_authorized_sources(frozen_sha256, verdict_bytes, report_bytes)
    snapshot = install_snapshot(payloads)
    gate = build_consumer_gate(snapshot)
    gate_payload = (json.dumps(gate, ensure_ascii=False, indent=2) + "\n").encode()
    m9 = consumer.original_controller()
    if consumer.CONSUMER_GATE.exists():
        receipt, existing, existing_payload = m9.read_d018_control_json(consumer.CONSUMER_GATE)
        if existing != gate or existing_payload != gate_payload:
            raise SystemExit("existing consumer gate differs")
    else:
        m9.atomic_owned_durable_bytes(
            consumer.CONSUMER_GATE,
            gate_payload,
            expected_uid=0,
            expected_gid=1000,
            expected_mode=0o640,
        )
        receipt, _, _ = m9.read_d018_control_json(consumer.CONSUMER_GATE)
    print(json.dumps({"status": "consumer_gate_installed", "receipt": receipt}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
