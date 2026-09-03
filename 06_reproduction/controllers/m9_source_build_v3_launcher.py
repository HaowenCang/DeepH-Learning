#!/usr/bin/env python3
"""One-shot source-only launcher for an issued M9 overlap capability."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import traceback


PROJECT_ROOT = Path("/mnt/e/Projects/Codex/DeepH")
FROZEN_HASHES = (
    PROJECT_ROOT
    / "06_reproduction/manifests/m9_overlap_py39_recovery_frozen_hashes.json"
)
CAPABILITY_ROOT = Path("/home/evan-williams/deeph-m9/manifests/overlap_capabilities")
CONTROL_DIRECTORY = PROJECT_ROOT / "06_reproduction/scripts"
BOOTSTRAP_MODULE_NAMES = ("argparse", "hashlib", "json", "pathlib")
LOCAL_MODULES = {
    "m9_overlap_common",
    "m9_openmx_build",
    "m9_openmx_input",
    "m9_overlap_contract",
    "m9_overlap_executor",
}
LOADED_SOURCES: dict[str, dict[str, object]] = {}
DEPENDENCY_PATH_PROVENANCE: dict[str, object] | None = None
SNAPSHOT = Path('/home/evan-williams/deeph-m9/controls/source-build-v3')
CONSUMER_NAME = 'm9_source_build_v3_consumer.py'
SELF_NAME = 'm9_source_build_v3_launcher.py'
CONSUMER = None
REPAIR = None
V3_BINDING = None


def pinned(path, expected=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        with os.fdopen(os.dup(fd), 'rb') as stream:
            data = stream.read()
        after, linked = os.fstat(fd), os.lstat(path)
        fields = ('st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_mode', 'st_nlink',
                  'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or (before.st_uid, before.st_gid, stat.S_IMODE(before.st_mode)) != (0, 1000, 0o440)
                or any(getattr(before, k) != getattr(after, k) or getattr(after, k) != getattr(linked, k)
                       for k in fields) or len(data) != before.st_size
                or expected is not None and hashlib.sha256(data).hexdigest() != expected):
            raise RuntimeError('v3 installed source identity differs: ' + str(path))
        return data
    finally:
        os.close(fd)


def installed_authority():
    global CONSUMER, REPAIR, V3_BINDING
    if Path(__file__) != SNAPSHOT / SELF_NAME or os.geteuid() != 1000:
        raise RuntimeError('v3 launcher requires installed path and real UID1000')
    metadata = os.lstat(SNAPSHOT)
    if (not stat.S_ISDIR(metadata.st_mode)
            or (metadata.st_uid, metadata.st_gid, stat.S_IMODE(metadata.st_mode)) != (0, 1000, 0o550)):
        raise RuntimeError('v3 launcher snapshot identity differs')
    manifest = json.loads(pinned(SNAPSHOT / 'snapshot_manifest.json'))
    if set(manifest) != {'schema', 'members'} or manifest['schema'] != 'm9-source-build-snapshot-v3':
        raise RuntimeError('v3 launcher snapshot schema differs')
    self_bytes = pinned(SNAPSHOT / SELF_NAME, manifest['members'][SELF_NAME]['sha256'])
    data = pinned(SNAPSHOT / CONSUMER_NAME, manifest['members'][CONSUMER_NAME]['sha256'])
    spec = importlib.util.spec_from_file_location('m9_v3_launch_consumer', SNAPSHOT / CONSUMER_NAME)
    c = importlib.util.module_from_spec(spec); sys.modules[spec.name] = c
    exec(compile(data, str(SNAPSHOT / CONSUMER_NAME), 'exec', dont_inherit=True), c.__dict__)
    c.fixed_runtime()
    binding = c.execution_binding()
    if (binding['consumer_sha256'] != sha256_bytes(data)
            or binding['launcher_sha256'] != sha256_bytes(self_bytes)):
        raise RuntimeError('v3 launcher self-consumer binding differs')
    repair_path = SNAPSHOT / c.REPAIR.name
    repair = c.load_bytes('m9_v3_launch_repair', repair_path, pinned(repair_path, c.REPAIR_SHA))
    CONSUMER, REPAIR, V3_BINDING = c, repair, binding
    return binding


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def isolated_bootstrap_provenance() -> dict[str, object]:
    if not sys.flags.isolated or not sys.flags.no_site or not sys.dont_write_bytecode:
        raise RuntimeError("formal source launcher requires frozen Python with -I -S -B")
    script_directory = Path(__file__).resolve().parent
    current_directory = Path.cwd().resolve()
    resolved_sys_path = []
    for raw in sys.path:
        if not raw:
            raise RuntimeError("empty current-directory entry is forbidden on launcher sys.path")
        resolved = Path(raw).resolve(strict=False)
        if resolved in (script_directory, current_directory):
            raise RuntimeError("script/current directory is forbidden on launcher sys.path")
        if "site-packages" in resolved.parts:
            raise RuntimeError("site-packages is forbidden on launcher bootstrap sys.path")
        resolved_sys_path.append(resolved.as_posix())
    stdlib_root = Path(sys.prefix) / f"lib/python{sys.version_info.major}.{sys.version_info.minor}"
    modules: dict[str, object] = {}
    for name in BOOTSTRAP_MODULE_NAMES:
        module = sys.modules.get(name)
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        loader = getattr(spec, "loader", None)
        if not isinstance(origin, str) or origin in ("built-in", "frozen"):
            raise RuntimeError(f"bootstrap module lacks frozen stdlib source origin: {name}")
        resolved_origin = Path(origin).resolve(strict=True)
        if stdlib_root.resolve() not in resolved_origin.parents or "site-packages" in resolved_origin.parts:
            raise RuntimeError(f"bootstrap module escaped frozen stdlib: {name} -> {resolved_origin}")
        modules[name] = {
            "loader": type(loader).__name__,
            "origin": resolved_origin.as_posix(),
            "sha256": sha256_bytes(resolved_origin.read_bytes()),
        }
    return {
        "isolated": True,
        "no_site": True,
        "dont_write_bytecode": True,
        "python_executable": Path(sys.executable).resolve(strict=True).as_posix(),
        "sys_path": resolved_sys_path,
        "modules": modules,
    }


def verify_control_directory(
    directory: Path = CONTROL_DIRECTORY,
    allowed_python: set[str] | None = None,
) -> None:
    if allowed_python is None:
        manifest = json.loads(FROZEN_HASHES.read_text(encoding="utf-8"))
        files = manifest.get("files")
        if not isinstance(files, dict):
            raise RuntimeError("frozen hash manifest lacks files")
        allowed_python = {
            Path(str(path)).name
            for path in files
            if Path(str(path)).parent.resolve(strict=False) == directory.resolve(strict=False)
            and Path(str(path)).suffix == ".py"
        }
    actual_python: set[str] = set()
    for entry in directory.iterdir():
        if entry.is_symlink() or entry.is_dir() or entry.suffix in (".pyc", ".pyo"):
            raise RuntimeError(f"cache, symlink, or subdirectory forbidden in control directory: {entry}")
        if entry.suffix != ".py" or entry.name not in allowed_python:
            raise RuntimeError(f"unfrozen control-directory file: {entry}")
        actual_python.add(entry.name)
    if actual_python != allowed_python:
        raise RuntimeError("frozen control-directory Python file set mismatch")


def append_dependency_path(contract: dict[str, object]) -> dict[str, object]:
    global DEPENDENCY_PATH_PROVENANCE
    execution = contract.get("execution")
    if not isinstance(execution, dict):
        raise RuntimeError("contract lacks execution policy")
    raw = execution.get("dependency_site_packages")
    if not isinstance(raw, str):
        raise RuntimeError("contract lacks frozen dependency site-packages")
    dependency = Path(raw)
    if dependency.is_symlink() or not dependency.is_dir():
        raise RuntimeError("frozen dependency site-packages is missing or a symlink")
    resolved = dependency.resolve(strict=True)
    expected = (
        Path(sys.prefix)
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    ).resolve(strict=True)
    if resolved != expected or resolved.as_posix() in sys.path:
        raise RuntimeError("dependency site-packages identity or bootstrap separation mismatch")
    sys.path.append(resolved.as_posix())
    DEPENDENCY_PATH_PROVENANCE = {
        "path": resolved.as_posix(),
        "added_after_capability": True,
        "method": "sys.path.append",
        "site_addsitedir_called": False,
        "pth_processed": False,
    }
    return DEPENDENCY_PATH_PROVENANCE


def atomic_json(path: Path, value: dict[str, object], mode: int = 0o600) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary, mode)
    os.replace(temporary, path)
    os.chmod(path, mode)


class FrozenSourceLoader(importlib.abc.Loader):
    def __init__(self, fullname: str, path: Path, expected_sha256: str) -> None:
        self.fullname = fullname
        self.path = path
        self.expected_sha256 = expected_sha256

    def create_module(self, spec: object) -> None:
        return None

    def exec_module(self, module: object) -> None:
        if CONSUMER is None or REPAIR is None:
            raise ImportError('v3 source load requires installed authority')
        raw = CONSUMER.read_bytes(self.path, self.expected_sha256)
        base_sha = sha256_bytes(raw)
        if self.fullname == 'm9_openmx_build':
            if self.path != CONSUMER.DRIVER or base_sha != CONSUMER.DRIVER_BASE_SHA:
                raise ImportError('v3 driver base identity differs')
            raw = REPAIR.derive(raw)
        actual = sha256_bytes(raw)
        source = raw.decode("utf-8")
        code = compile(source, self.path.as_posix(), "exec", dont_inherit=True)
        LOADED_SOURCES[self.fullname] = {
            "path": self.path.as_posix(),
            "sha256": actual,
            "loader": type(self).__name__,
            "origin": self.path.as_posix(),
            "bytecode_consulted": False,
        }
        if self.fullname == 'm9_openmx_build':
            LOADED_SOURCES[self.fullname]['base_sha256'] = base_sha
        exec(code, module.__dict__)  # type: ignore[attr-defined]


class FrozenSourceFinder(importlib.abc.MetaPathFinder):
    def __init__(self, mapping: dict[str, tuple[Path, str]]) -> None:
        self.mapping = mapping

    def find_spec(
        self, fullname: str, path: object = None, target: object = None
    ) -> object | None:
        item = self.mapping.get(fullname)
        if item is None:
            return None
        source_path, expected = item
        loader = FrozenSourceLoader(fullname, source_path, expected)
        return importlib.util.spec_from_loader(fullname, loader, origin=source_path.as_posix())


def frozen_module_mapping() -> dict[str, tuple[Path, str]]:
    manifest = json.loads(FROZEN_HASHES.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "m9-overlap-frozen-hashes-v1":
        raise RuntimeError("unexpected frozen hash manifest schema")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise RuntimeError("frozen hash manifest lacks files")
    mapping: dict[str, tuple[Path, str]] = {}
    for text_path, expected in files.items():
        path = Path(str(text_path))
        module = path.stem
        if module in LOCAL_MODULES:
            raw = path.read_bytes()
            if sha256_bytes(raw) != expected:
                raise RuntimeError(f"frozen module differs before source-only load: {path}")
            mapping[module] = (path, str(expected))
    if set(mapping) != LOCAL_MODULES:
        raise RuntimeError(f"frozen module set mismatch: {sorted(mapping)}")
    return mapping


def wait_and_consume_capability(capability_id: str) -> dict[str, object]:
    if not re.fullmatch(r"[0-9a-f]{32}", capability_id):
        raise RuntimeError("invalid capability ID")
    path = CAPABILITY_ROOT / f"{capability_id}.json"
    deadline = time.monotonic() + 10.0
    while not path.is_file() and time.monotonic() < deadline:
        time.sleep(0.01)
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("bound capability was not issued")
    stat = path.stat()
    if stat.st_uid != os.getuid() or stat.st_mode & 0o077:
        raise RuntimeError("capability owner/mode mismatch")
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("schema_version") != "m9-overlap-capability-v1"
        or value.get("state") != "BOUND"
        or value.get("capability_id") != capability_id
        or int(value.get("child_pid", -1)) != os.getpid()
        or int(value.get("budget_pid", -1)) != os.getppid()
    ):
        raise RuntimeError("capability binding mismatch")
    parent_cmdline = Path(f"/proc/{os.getppid()}/cmdline").read_bytes().split(b"\0")
    parent_argv = [item.decode("utf-8") for item in parent_cmdline if item]
    if value.get("budget_argv") != parent_argv:
        raise RuntimeError("capability is not bound to the live budget parent argv")
    expected_argv = [
        Path(sys.executable).resolve().as_posix(),
        "-I",
        "-S",
        "-B",
        Path(__file__).resolve().as_posix(),
        "--capability-id",
        capability_id,
    ]
    if value.get("launcher_argv") != expected_argv:
        raise RuntimeError("capability launcher argv mismatch")
    if CONSUMER is None or CONSUMER.execution_binding() != V3_BINDING:
        raise RuntimeError('v3 execution binding changed before capability consumption')
    parent_expected = [str(CONSUMER.PYTHON.resolve()), '-I', '-S', '-B',
                       str(SNAPSHOT / CONSUMER_NAME), *CONSUMER.RUN_ARGV]
    if (parent_argv != parent_expected or value.get('action') != 'source_build'
            or value.get('structure_id') is not None or value.get('bucket') != 'overlap_build'
            or value.get('forecast_bytes') != 4294967296):
        raise RuntimeError('v3 capability action or budget parent differs')
    consumed = dict(value)
    consumed["state"] = "CONSUMED"
    consumed["consumed_utc"] = utc_now()
    consumed_path = CAPABILITY_ROOT / f"{capability_id}.consumed.json"
    if consumed_path.exists():
        raise RuntimeError("capability was already consumed")
    atomic_json(consumed_path, consumed)
    path.unlink()
    return consumed


def dispatch(capability: dict[str, object]) -> object:
    finder = FrozenSourceFinder(frozen_module_mapping())
    sys.meta_path.insert(0, finder)
    for name in LOCAL_MODULES:
        sys.modules.pop(name, None)
    import m9_overlap_common as common

    common.install_budget_context(capability)
    contract, contract_hash = common.load_contract()
    append_dependency_path(contract)
    action = str(capability["action"])
    structure_id = capability.get("structure_id")
    if action == "source_prepare":
        import m9_openmx_build as controller

        return controller.prepare_sources(contract)
    if action == "source_build":
        import m9_openmx_build as controller

        return controller.build_sources(contract)
    if action in ("smoke_prepare", "batch_prepare"):
        import m9_overlap_executor as controller

        return controller.prepare(str(structure_id), contract, contract_hash)
    if action in ("smoke_run", "batch_run"):
        import m9_overlap_executor as controller

        return controller.run_structure(str(structure_id), contract, contract_hash)
    if action == "project":
        import m9_overlap_executor as controller

        return controller.project_batch(contract)
    raise RuntimeError(f"unsupported controller action: {action}")


def main() -> int:
    launcher_bootstrap = isolated_bootstrap_provenance()
    installed_authority()
    verify_control_directory()
    if len(sys.argv) != 3 or sys.argv[1] != '--capability-id' or not re.fullmatch(r'[0-9a-f]{32}', sys.argv[2]):
        raise RuntimeError('v3 launcher requires exact capability argv')
    capability_id = sys.argv[2]
    capability = wait_and_consume_capability(capability_id)
    receipt_path = CAPABILITY_ROOT / f"{capability_id}.launcher-receipt.json"
    try:
        result = dispatch(capability)
        receipt: dict[str, object] = {
            "schema_version": "m9-overlap-source-launcher-receipt-v1",
            "capability_id": capability_id,
            "transaction_id": capability["transaction_id"],
            "status": "PASS",
            "budget_bootstrap": capability["budget_bootstrap"],
            "launcher_bootstrap": launcher_bootstrap,
            "dependency_path": DEPENDENCY_PATH_PROVENANCE,
            "loaded_sources": LOADED_SOURCES,
            "v3_binding": V3_BINDING,
            "completed_utc": utc_now(),
        }
        atomic_json(receipt_path, receipt)
        print(json.dumps({"launcher_receipt": receipt, "result": result}, sort_keys=True))
        return 0
    except BaseException as exc:
        receipt = {
            "schema_version": "m9-overlap-source-launcher-receipt-v1",
            "capability_id": capability_id,
            "transaction_id": capability["transaction_id"],
            "status": "FAIL",
            "budget_bootstrap": capability["budget_bootstrap"],
            "launcher_bootstrap": launcher_bootstrap,
            "dependency_path": DEPENDENCY_PATH_PROVENANCE,
            "loaded_sources": LOADED_SOURCES,
            "v3_binding": V3_BINDING,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "completed_utc": utc_now(),
        }
        atomic_json(receipt_path, receipt)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
