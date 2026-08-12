#!/usr/bin/env python3
"""Hard-stop budget ledger for the frozen M9 reproduction.

This script has no third-party dependencies. It is intended to be invoked from
Ubuntu-22.04 through WSL for every mutating or GPU-using M9 command.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from typing import Iterable


LINUX_ROOT = Path("/home/evan-williams/deeph-m9")
MANIFESTS = LINUX_ROOT / "manifests"
STATE_PATH = MANIFESTS / "budget_state.json"
LEDGER_PATH = MANIFESTS / "budget_ledger.jsonl"
LOCK_PATH = MANIFESTS / "budget.lock"
PROJECT_ROOT = Path("/mnt/e/Projects/Codex/DeepH")
REPRODUCTION = PROJECT_ROOT / "06_reproduction"
AUDITS = PROJECT_ROOT / "08_audits"
CONTROL_FILES = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "decisions.md",
    PROJECT_ROOT / "00_scope/master_execution_plan.md",
    PROJECT_ROOT / "00_scope/M8_decision_package.md",
    PROJECT_ROOT / "02_source_ledger/version_registry.md",
    PROJECT_ROOT / "08_audits/progress_tracker.md",
)
HOST_VHDX = Path("/mnt/e/Laptop/WSL/ext4.vhdx")

WALL_LIMIT = 604800.0
GPU_LIMITS = {
    "compatibility": 7200.0,
    "training": 57600.0,
    "physical_validation": 21600.0,
}
GPU_TOTAL_LIMIT = 86400.0
CPU_LIMITS = {
    "overlap_build": 7200.0,
    "overlap_smoke": 1800.0,
    "overlap_batch": 21600.0,
}
STORAGE_LIMIT = 107374182400
PROJECT_SUBLIMIT = 1073741824
FROZEN_START = "2026-08-11T14:50:05.7533015Z"
FROZEN_DEADLINE = "2026-08-18T14:50:05.7533015Z"
FROZEN_VHDX_BASELINE = 1488977920


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> dt.datetime:
    normalized = value.replace("Z", "+00:00")
    normalized = re.sub(r"(\.\d{6})\d+(?=[+-]\d\d:\d\d$)", r"\1", normalized)
    return dt.datetime.fromisoformat(normalized)


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def path_usage(path: Path) -> tuple[int, int]:
    """Return apparent and allocated bytes without following symlinks."""
    if not path.exists() and not path.is_symlink():
        return 0, 0
    apparent = 0
    allocated = 0
    paths: Iterable[Path]
    if path.is_dir() and not path.is_symlink():
        paths = (Path(root) / name for root, dirs, files in os.walk(path, followlinks=False)
                 for name in files)
    else:
        paths = (path,)
    for item in paths:
        try:
            stat = item.lstat()
        except FileNotFoundError:
            continue
        apparent += stat.st_size
        allocated += stat.st_blocks * 512
    return apparent, allocated


def project_usage() -> tuple[int, int]:
    apparent, allocated = path_usage(REPRODUCTION)
    if AUDITS.exists():
        for item in AUDITS.iterdir():
            if item.is_file() and item.name.startswith("M9_"):
                a, b = path_usage(item)
                apparent += a
                allocated += b
    for item in CONTROL_FILES:
        a, b = path_usage(item)
        apparent += a
        allocated += b
    return apparent, allocated


def storage_snapshot(state: dict) -> dict:
    linux_a, linux_b = path_usage(LINUX_ROOT)
    project_a, project_b = project_usage()
    vhdx_size = None
    vhdx_growth = None
    try:
        vhdx_size = HOST_VHDX.stat().st_size
        vhdx_growth = max(0, vhdx_size - int(state["vhdx_baseline_bytes"]))
    except OSError:
        pass
    return {
        "linux_apparent_bytes": linux_a,
        "linux_allocated_bytes": linux_b,
        "project_audit_apparent_bytes": project_a,
        "project_audit_allocated_bytes": project_b,
        "combined_apparent_bytes": linux_a + project_a,
        "combined_allocated_bytes": linux_b + project_b,
        "host_vhdx_bytes": vhdx_size,
        "host_vhdx_growth_from_start_bytes": vhdx_growth,
    }


def preserve_owner(path: Path) -> None:
    if os.geteuid() == 0:
        os.chown(path, 1000, 1000)


def atomic_json(path: Path, value: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preserve_owner(tmp)
    os.replace(tmp, path)
    preserve_owner(path)


def append_event(event: dict) -> None:
    with LEDGER_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    preserve_owner(LEDGER_PATH)


def initial_state() -> dict:
    return {
        "schema_version": "m9-budget-state-v1",
        "start_utc": FROZEN_START,
        "deadline_utc": FROZEN_DEADLINE,
        "vhdx_baseline_bytes": FROZEN_VHDX_BASELINE,
        "gpu_seconds": {name: 0.0 for name in GPU_LIMITS},
        "cpu_seconds": {name: 0.0 for name in CPU_LIMITS},
        "last_event_utc": FROZEN_START,
        "hard_stopped": False,
    }


def load_state() -> dict:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state.setdefault("cpu_seconds", {name: 0.0 for name in CPU_LIMITS})
    for name in CPU_LIMITS:
        state["cpu_seconds"].setdefault(name, 0.0)
    return state


def deadline_remaining(state: dict) -> float:
    return (parse_utc(state["deadline_utc"]) - dt.datetime.now(dt.timezone.utc)).total_seconds()


def violations(state: dict, forecast_bytes: int = 0) -> list[str]:
    result: list[str] = []
    if state.get("hard_stopped"):
        result.append("ledger_already_hard_stopped")
    remaining = deadline_remaining(state)
    if remaining <= 0:
        result.append("wall_clock_limit")
    snap = storage_snapshot(state)
    if snap["project_audit_apparent_bytes"] > PROJECT_SUBLIMIT:
        result.append("project_audit_sublimit")
    for key in ("combined_apparent_bytes", "combined_allocated_bytes"):
        if snap[key] + forecast_bytes > STORAGE_LIMIT:
            result.append(key)
    growth = snap["host_vhdx_growth_from_start_bytes"]
    if growth is not None and growth + forecast_bytes > STORAGE_LIMIT:
        result.append("host_vhdx_growth_from_start_bytes")
    for bucket, limit in GPU_LIMITS.items():
        if float(state["gpu_seconds"][bucket]) >= limit:
            result.append(f"gpu_bucket_{bucket}")
    if sum(float(x) for x in state["gpu_seconds"].values()) >= GPU_TOTAL_LIMIT:
        result.append("gpu_total")
    for bucket, limit in CPU_LIMITS.items():
        if float(state["cpu_seconds"][bucket]) >= limit:
            result.append(f"cpu_bucket_{bucket}")
    return result


def hard_stop(state: dict, reasons: list[str], command_hash: str | None = None) -> None:
    state["hard_stopped"] = True
    state["last_event_utc"] = utc_now()
    atomic_json(STATE_PATH, state)
    append_event({
        "event": "HARD_STOP",
        "utc": state["last_event_utc"],
        "reasons": reasons,
        "command_sha256": command_hash,
        "storage": storage_snapshot(state),
        "gpu_seconds": state["gpu_seconds"],
        "cpu_seconds": state["cpu_seconds"],
    })


def command_init(_: argparse.Namespace) -> int:
    for name in ("software", "data/downloads", "data/graphene", "env", "runs", "manifests", "logs"):
        (LINUX_ROOT / name).mkdir(parents=True, exist_ok=True)
    if STATE_PATH.exists() or LEDGER_PATH.exists():
        raise SystemExit("budget state already exists; refusing to reinitialize")
    state = initial_state()
    atomic_json(STATE_PATH, state)
    snap = storage_snapshot(state)
    append_event({
        "event": "BUDGET_START",
        "utc": FROZEN_START,
        "deadline_utc": FROZEN_DEADLINE,
        "storage": snap,
        "gpu_seconds": state["gpu_seconds"],
        "cpu_seconds": state["cpu_seconds"],
    })
    print(json.dumps({"status": "initialized", "storage": snap}, sort_keys=True))
    return 0


def command_status(_: argparse.Namespace) -> int:
    state = load_state()
    payload = {
        "deadline_remaining_seconds": deadline_remaining(state),
        "gpu_seconds": state["gpu_seconds"],
        "cpu_seconds": state["cpu_seconds"],
        "storage": storage_snapshot(state),
        "violations": violations(state),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if not payload["violations"] else 2


def command_run(args: argparse.Namespace) -> int:
    if not args.command:
        raise SystemExit("missing command after --")
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("a+") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        state = load_state()
        command = args.command
        command_hash = canonical_hash(command)
        config_hash = None
        if args.config:
            config_hash = hashlib.sha256(Path(args.config).read_bytes()).hexdigest()
        before_reasons = violations(state, args.forecast_bytes)
        if args.bucket != "none":
            used = float(state["gpu_seconds"][args.bucket])
            if used >= GPU_LIMITS[args.bucket]:
                before_reasons.append(f"gpu_bucket_{args.bucket}")
        if args.cpu_bucket != "none":
            used = float(state["cpu_seconds"][args.cpu_bucket])
            if used >= CPU_LIMITS[args.cpu_bucket]:
                before_reasons.append(f"cpu_bucket_{args.cpu_bucket}")
        if before_reasons:
            hard_stop(state, sorted(set(before_reasons)), command_hash)
            print(json.dumps({"status": "hard_stop", "reasons": before_reasons}), file=sys.stderr)
            return 125
        wall_remaining = deadline_remaining(state)
        timeout_seconds = wall_remaining
        if args.bucket != "none":
            timeout_seconds = min(timeout_seconds, GPU_LIMITS[args.bucket] - float(state["gpu_seconds"][args.bucket]))
        if args.cpu_bucket != "none":
            timeout_seconds = min(
                timeout_seconds,
                CPU_LIMITS[args.cpu_bucket] - float(state["cpu_seconds"][args.cpu_bucket]),
            )
        start_utc = utc_now()
        start_ns = time.monotonic_ns()
        capture_output = args.log is not None
        proc = subprocess.Popen(
            command,
            cwd=args.cwd or str(LINUX_ROOT),
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.STDOUT if capture_output else None,
        )
        timed_out = False
        output = b""
        try:
            if capture_output:
                output, _ = proc.communicate(timeout=max(1.0, timeout_seconds))
                exit_code = proc.returncode
            else:
                exit_code = proc.wait(timeout=max(1.0, timeout_seconds))
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.send_signal(signal.SIGTERM)
            try:
                if capture_output:
                    tail, _ = proc.communicate(timeout=30)
                    output += tail or b""
                    exit_code = proc.returncode
                else:
                    exit_code = proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                if capture_output:
                    tail, _ = proc.communicate()
                    output += tail or b""
                    exit_code = proc.returncode
                else:
                    exit_code = proc.wait()
        if capture_output:
            log_path = Path(args.log)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_bytes(output)
            preserve_owner(log_path)
            sys.stdout.buffer.write(output)
            sys.stdout.buffer.flush()
        end_ns = time.monotonic_ns()
        end_utc = utc_now()
        elapsed = (end_ns - start_ns) / 1_000_000_000.0
        if args.bucket != "none":
            state["gpu_seconds"][args.bucket] = float(state["gpu_seconds"][args.bucket]) + elapsed
        if args.cpu_bucket != "none":
            state["cpu_seconds"][args.cpu_bucket] = (
                float(state["cpu_seconds"][args.cpu_bucket]) + elapsed
            )
        state["last_event_utc"] = end_utc
        atomic_json(STATE_PATH, state)
        event = {
            "event": "COMMAND",
            "bucket": args.bucket,
            "cpu_bucket": args.cpu_bucket,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "start_monotonic_ns": start_ns,
            "end_monotonic_ns": end_ns,
            "elapsed_seconds": elapsed,
            "pid": proc.pid,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "command_sha256": command_hash,
            "config_sha256": config_hash,
            "log_path": args.log,
            "log_sha256": hashlib.sha256(output).hexdigest() if capture_output else None,
            "forecast_bytes": args.forecast_bytes,
            "gpu_seconds": state["gpu_seconds"],
            "cpu_seconds": state["cpu_seconds"],
            "storage": storage_snapshot(state),
        }
        append_event(event)
        after_reasons = violations(state)
        if timed_out or after_reasons:
            reasons = (["command_timeout"] if timed_out else []) + after_reasons
            hard_stop(state, sorted(set(reasons)), command_hash)
            return 124 if timed_out else 125
        return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    init = sub.add_parser("init")
    init.set_defaults(func=command_init)
    status = sub.add_parser("status")
    status.set_defaults(func=command_status)
    run = sub.add_parser("run")
    run.add_argument("--bucket", choices=("none", *GPU_LIMITS), required=True)
    run.add_argument("--cpu-bucket", choices=("none", *CPU_LIMITS), default="none")
    run.add_argument("--forecast-bytes", type=int, default=0)
    run.add_argument("--config")
    run.add_argument("--log")
    run.add_argument("--cwd")
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(func=command_run)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if getattr(args, "command", None) and args.command[0] == "--":
        args.command = args.command[1:]
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
