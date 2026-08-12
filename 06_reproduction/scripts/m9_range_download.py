#!/usr/bin/env python3
"""Range-safe downloader for large immutable M9 artifacts.

Each chunk is fetched by a fresh curl process.  A chunk is accepted only when
the server returns HTTP 206 and the byte count exactly matches the requested
closed interval.  The final file is atomically installed only after its size
and expected MD5 match.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            hasher.update(block)
    return hasher.hexdigest()


def fetch_chunk(
    *,
    url: str,
    chunks_dir: Path,
    index: int,
    start: int,
    end: int,
    attempts: int,
) -> dict[str, object]:
    final_path = chunks_dir / f"{index:05d}-{start}-{end}.part"
    expected = end - start + 1
    if final_path.exists() and final_path.stat().st_size == expected:
        return {
            "index": index,
            "start": start,
            "end": end,
            "bytes": expected,
            "sha256": digest(final_path, "sha256"),
            "reused": True,
        }

    tmp_path = final_path.with_suffix(".tmp")
    for attempt in range(1, attempts + 1):
        if tmp_path.exists():
            tmp_path.unlink()
        command = [
            "curl",
            "-fL",
            "--silent",
            "--show-error",
            "--connect-timeout",
            "30",
            "--max-time",
            "600",
            "--speed-time",
            "120",
            "--speed-limit",
            "1024",
            "--range",
            f"{start}-{end}",
            "--output",
            str(tmp_path),
            "--write-out",
            "%{http_code}",
            url,
        ]
        completed = subprocess.run(command, text=True, capture_output=True)
        actual = tmp_path.stat().st_size if tmp_path.exists() else -1
        status = completed.stdout.strip()
        if completed.returncode == 0 and status == "206" and actual == expected:
            os.replace(tmp_path, final_path)
            record = {
                "index": index,
                "start": start,
                "end": end,
                "bytes": expected,
                "sha256": digest(final_path, "sha256"),
                "reused": False,
            }
            print(json.dumps({"chunk_complete": record}, sort_keys=True), flush=True)
            return record
        print(
            json.dumps(
                {
                    "chunk_retry": {
                        "index": index,
                        "attempt": attempt,
                        "curl_returncode": completed.returncode,
                        "http_status": status,
                        "actual_bytes": actual,
                        "expected_bytes": expected,
                        "stderr": completed.stderr.strip()[-500:],
                    }
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        if attempt < attempts:
            time.sleep(3)
    raise RuntimeError(f"chunk {index} failed after {attempts} attempts")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-bytes", type=int, required=True)
    parser.add_argument("--expected-md5", required=True)
    parser.add_argument("--chunk-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--attempts", type=int, default=20)
    args = parser.parse_args()

    if args.expected_bytes <= 0 or args.chunk_bytes <= 0:
        raise ValueError("byte counts must be positive")
    if args.workers < 1 or args.attempts < 1:
        raise ValueError("workers and attempts must be positive")
    expected_md5 = args.expected_md5.lower()
    if len(expected_md5) != 32 or any(c not in "0123456789abcdef" for c in expected_md5):
        raise ValueError("expected MD5 must be 32 lowercase hex characters")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    chunks_dir = args.output.parent / f"{args.output.name}.chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output.parent / f"{args.output.name}.chunks.json"

    if args.output.exists():
        if args.output.stat().st_size == args.expected_bytes and digest(args.output, "md5") == expected_md5:
            print(json.dumps({"already_complete": str(args.output)}, sort_keys=True))
            return 0
        raise RuntimeError("output exists but does not match the frozen size and MD5")

    ranges = []
    for index, start in enumerate(range(0, args.expected_bytes, args.chunk_bytes)):
        end = min(args.expected_bytes - 1, start + args.chunk_bytes - 1)
        ranges.append((index, start, end))

    records: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(
                fetch_chunk,
                url=args.url,
                chunks_dir=chunks_dir,
                index=index,
                start=start,
                end=end,
                attempts=args.attempts,
            )
            for index, start, end in ranges
        ]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())

    records.sort(key=lambda item: int(item["index"]))
    assembling = args.output.with_suffix(args.output.suffix + ".assembling")
    if assembling.exists():
        assembling.unlink()
    with assembling.open("xb") as destination:
        for record in records:
            part = chunks_dir / (
                f"{int(record['index']):05d}-{int(record['start'])}-{int(record['end'])}.part"
            )
            with part.open("rb") as source:
                while block := source.read(8 * 1024 * 1024):
                    destination.write(block)
        destination.flush()
        os.fsync(destination.fileno())

    actual_bytes = assembling.stat().st_size
    actual_md5 = digest(assembling, "md5")
    actual_sha256 = digest(assembling, "sha256")
    if actual_bytes != args.expected_bytes or actual_md5 != expected_md5:
        raise RuntimeError(
            f"assembled artifact mismatch: bytes={actual_bytes}, md5={actual_md5}"
        )

    manifest = {
        "schema_version": "m9-range-download-v1",
        "url": args.url,
        "output": str(args.output),
        "bytes": actual_bytes,
        "md5": actual_md5,
        "sha256": actual_sha256,
        "chunk_bytes": args.chunk_bytes,
        "workers": args.workers,
        "chunks": records,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(assembling, args.output)
    print(json.dumps({"complete": manifest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
