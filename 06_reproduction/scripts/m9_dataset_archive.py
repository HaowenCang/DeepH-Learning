#!/usr/bin/env python3
"""Validate, extract, and inventory the frozen M9 ZIP dataset safely."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import zipfile


COPY_BLOCK_BYTES = 8 * 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(COPY_BLOCK_BYTES):
            digest.update(block)
    return digest.hexdigest()


def validate_members(archive: zipfile.ZipFile) -> tuple[list[zipfile.ZipInfo], dict[str, object]]:
    members = archive.infolist()
    if not members:
        raise ValueError("archive is empty")

    normalized: set[str] = set()
    top_levels: set[str] = set()
    file_count = 0
    directory_count = 0
    compressed_bytes = 0
    uncompressed_bytes = 0

    for info in members:
        name = info.filename
        if not name or "\x00" in name:
            raise ValueError(f"invalid empty or NUL-containing member name: {name!r}")
        if "\\" in name or name.startswith("/") or re.match(r"^[A-Za-z]:", name):
            raise ValueError(f"non-portable or absolute member name: {name!r}")
        path = PurePosixPath(name)
        if any(part in {"", ".", ".."} for part in path.parts):
            raise ValueError(f"non-canonical member path: {name!r}")
        canonical = path.as_posix().rstrip("/")
        if canonical in normalized:
            raise ValueError(f"duplicate normalized member path: {canonical!r}")
        normalized.add(canonical)
        top_levels.add(path.parts[0])
        if info.flag_bits & 0x1:
            raise ValueError(f"encrypted member is forbidden: {name!r}")

        unix_mode = (info.external_attr >> 16) & 0xFFFF
        file_type = stat.S_IFMT(unix_mode)
        if file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
            raise ValueError(f"link or special-file member is forbidden: {name!r}")

        if info.is_dir():
            directory_count += 1
        else:
            file_count += 1
            compressed_bytes += info.compress_size
            uncompressed_bytes += info.file_size

    summary: dict[str, object] = {
        "schema_version": "m9-archive-inspection-v1",
        "member_count": len(members),
        "file_count": file_count,
        "directory_count": directory_count,
        "compressed_member_bytes": compressed_bytes,
        "uncompressed_bytes": uncompressed_bytes,
        "top_level_paths": sorted(top_levels),
    }
    return members, summary


def inspect_archive(archive_path: Path) -> dict[str, object]:
    with zipfile.ZipFile(archive_path, "r") as archive:
        _members, summary = validate_members(archive)
        corrupt = archive.testzip()
        if corrupt is not None:
            raise ValueError(f"CRC failure in archive member: {corrupt!r}")
    summary["archive"] = str(archive_path)
    summary["archive_bytes"] = archive_path.stat().st_size
    summary["archive_sha256"] = sha256(archive_path)
    return summary


def extract_archive(archive_path: Path, destination: Path) -> dict[str, object]:
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    staging = destination.with_name(destination.name + ".extracting")
    if staging.exists():
        raise FileExistsError(f"staging destination already exists: {staging}")
    staging.mkdir(parents=True)

    written_files = 0
    written_bytes = 0
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            members, summary = validate_members(archive)
            for info in members:
                relative = PurePosixPath(info.filename)
                target = staging.joinpath(*relative.parts)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    raise FileExistsError(f"refusing to overwrite extracted path: {target}")
                with archive.open(info, "r") as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=COPY_BLOCK_BYTES)
                    output.flush()
                    os.fsync(output.fileno())
                if target.stat().st_size != info.file_size:
                    raise ValueError(f"extracted size mismatch: {info.filename!r}")
                written_files += 1
                written_bytes += info.file_size
        os.replace(staging, destination)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise

    return {
        **summary,
        "archive": str(archive_path),
        "destination": str(destination),
        "written_files": written_files,
        "written_bytes": written_bytes,
    }


def inventory_tree(root: Path) -> dict[str, object]:
    if not root.is_dir():
        raise NotADirectoryError(root)
    records: list[dict[str, object]] = []
    total_bytes = 0
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        records.append({"path": relative, "bytes": size, "sha256": sha256(path)})
        total_bytes += size
    return {
        "schema_version": "m9-dataset-inventory-v1",
        "root": str(root),
        "file_count": len(records),
        "total_bytes": total_bytes,
        "files": records,
    }


def emit(payload: dict[str, object], output: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    os.replace(temporary, output)
    print(json.dumps({"written": str(output), "bytes": output.stat().st_size}, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--archive", type=Path, required=True)
    inspect_parser.add_argument("--output", type=Path)

    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("--archive", type=Path, required=True)
    extract_parser.add_argument("--destination", type=Path, required=True)
    extract_parser.add_argument("--output", type=Path)

    inventory_parser = subparsers.add_parser("inventory")
    inventory_parser.add_argument("--root", type=Path, required=True)
    inventory_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "inspect":
        emit(inspect_archive(args.archive), args.output)
    elif args.command == "extract":
        emit(extract_archive(args.archive, args.destination), args.output)
    else:
        emit(inventory_tree(args.root), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
