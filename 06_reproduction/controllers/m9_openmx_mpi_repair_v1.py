"""Pinned source derivation and read-only real-toolchain check; never builds."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
ROOT = Path('/home/evan-williams/deeph-m9')
SNAPSHOT = ROOT / 'controls/source-build-mpi-repair-v1'
BASE = PROJECT / '06_reproduction/scripts/m9_openmx_build.py'
COMMON = PROJECT / '06_reproduction/scripts/m9_overlap_common.py'
CONTRACT = PROJECT / '06_reproduction/configs/m9_overlap_only_contract.json'
BASE_SHA = 'ab6632784a744fd3f66c95aac30a56767f67af3d8d81147df2fc0d72b67102ec'
COMMON_SHA = 'fc8c16ed37072c6410c1d4bc942716fad66be4d3d22c2f72cc299b7fce55e07f'
CONTRACT_SHA = 'a0e6d017f568e5caa7fe7a49939330c88263058066af14ce8809ef625b36abb0'
DERIVED_SHA = '5652ee35a3595f42bd3050e5825419175fc84526a421a0500559d4146f253d00'
OLD = b'        if output != toolchain[name]:\n'
NEW = b'''        expected = toolchain[name]
        if name == "openmpi_showme_version":
            if command[0] != "/usr/bin/mpicc" or expected != "mpicc: Open MPI 4.1.2 (Language: C)":
                raise ValueError("OpenMPI frozen command or comparison contract differs")
            expected = "/usr/bin/" + expected
        if output != expected:
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, digest, owner=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        first = os.fstat(fd)
        with os.fdopen(os.dup(fd), 'rb') as stream:
            data = stream.read()
        second, linked = os.fstat(fd), os.lstat(path)
        keys = ('st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_mode', 'st_nlink',
                'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if (not stat.S_ISREG(first.st_mode) or first.st_nlink != 1
                or any(getattr(first, k) != getattr(second, k) or getattr(second, k) != getattr(linked, k) for k in keys)
                or len(data) != first.st_size or digest is not None and sha(data) != digest
                or owner is not None and (first.st_uid, first.st_gid, stat.S_IMODE(first.st_mode)) != owner):
            raise ValueError('pinned source differs: ' + str(path))
        return data
    finally:
        os.close(fd)


def derive(data):
    if sha(data) != BASE_SHA or data.count(OLD) != 1:
        raise ValueError('MPI repair base or exact match differs')
    result = data.replace(OLD, NEW, 1)
    if sha(result) != DERIVED_SHA or result.count(NEW) != 1 or result.replace(NEW, OLD, 1) != data:
        raise ValueError('MPI repair is not an exact reversible derivation')
    return result


def load_source(name, origin, data):
    spec = importlib.util.spec_from_file_location(name, origin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(data, str(origin), 'exec', dont_inherit=True), module.__dict__)
    return module


def source_payloads():
    installed = Path(__file__).parent == SNAPSHOT
    owner = (0, 1000, 0o440) if installed else None
    if installed:
        directory = os.lstat(SNAPSHOT)
        if not stat.S_ISDIR(directory.st_mode) or (directory.st_uid, directory.st_gid, stat.S_IMODE(directory.st_mode)) != (0, 1000, 0o550):
            raise ValueError('repair snapshot security differs')
        manifest = json.loads(pinned(SNAPSHOT / 'snapshot_manifest.json', None, owner))
        names = {'m9_openmx_mpi_repair_v1.py', 'm9_openmx_build.original.py',
                 'm9_overlap_common.py', 'm9_overlap_only_contract.json'}
        if (set(manifest) != {'schema', 'members'} or manifest['schema'] != 'm9-mpi-repair-snapshot-v1'
                or set(manifest['members']) != names
                or {p.name for p in SNAPSHOT.iterdir()} != names | {'snapshot_manifest.json'}):
            raise ValueError('repair snapshot closure differs')
        for name, item in manifest['members'].items():
            data = pinned(SNAPSHOT / name, item['sha256'], owner)
            if set(item) != {'bytes', 'sha256'} or len(data) != item['bytes']:
                raise ValueError('repair snapshot member differs')
    paths = ((BASE, 'm9_openmx_build.original.py', BASE_SHA),
             (COMMON, 'm9_overlap_common.py', COMMON_SHA),
             (CONTRACT, 'm9_overlap_only_contract.json', CONTRACT_SHA))
    return [pinned(SNAPSHOT / name if installed else path, digest, owner)
            for path, name, digest in paths]


def verify_toolchain():
    base, common, contract_raw = source_payloads()
    derived = derive(base)
    # Dedicated read-only process: never install a capability or invoke build_sources.
    load_source('m9_overlap_common', COMMON, common)
    driver = load_source('m9_openmx_build', SNAPSHOT / 'm9_openmx_build.repaired.py', derived)
    packages = driver.verify_packages(json.loads(contract_raw))
    return {'status': 'PASS', 'build_executed': False, 'base_sha256': sha(base),
            'derived_sha256': sha(derived), 'packages': packages}


def main():
    if sys.argv[1:] != ['verify-toolchain']:
        raise SystemExit('only read-only verify-toolchain is supported; no build/run/recovery')
    if (os.geteuid() != 1000 or sys.version_info[:3] != (3, 9, 23)
            or Path(sys.executable).resolve() != (ROOT / 'env/deeph-v022/bin/python3.9').resolve()
            or not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode)):
        raise SystemExit('requires real UID1000 frozen Python3.9.23 -I -S -B')
    print(json.dumps(verify_toolchain(), sort_keys=True))


if __name__ == '__main__':
    main()
