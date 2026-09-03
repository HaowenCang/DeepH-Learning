"""Real call-site regression; run with frozen Linux Python3.9 -I -S -B."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
import tempfile

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
PATH = PROJECT / '06_reproduction/controllers/m9_openmx_mpi_repair_v1.py'
spec = importlib.util.spec_from_file_location('repair', PATH)
r = importlib.util.module_from_spec(spec)
exec(compile(PATH.read_bytes(), str(PATH), 'exec', dont_inherit=True), r.__dict__)


def driver(repaired):
    raw = r.pinned(r.BASE, r.BASE_SHA)
    r.load_source('m9_overlap_common', r.COMMON, r.pinned(r.COMMON, r.COMMON_SHA))
    return r.load_source('m9_openmx_build', r.BASE, r.derive(raw) if repaired else raw)


class MPIRepairTests(unittest.TestCase):
    def test_original_real_absolute_call_reproduces_b01(self):
        with self.assertRaisesRegex(ValueError, "openmpi_showme_version='/usr/bin/mpicc:"):
            driver(False).verify_packages(json.loads(r.pinned(r.CONTRACT, r.CONTRACT_SHA)))

    def test_repaired_real_full_toolchain_passes(self):
        self.assertEqual(os.geteuid(), 1000)
        result = r.verify_toolchain()
        self.assertEqual(result['status'], 'PASS')
        self.assertFalse(result['build_executed'])
        self.assertEqual(result['packages']['openmpi_showme_version'], '/usr/bin/mpicc: Open MPI 4.1.2 (Language: C)')

    def test_only_verify_packages_ast_changes_and_bytes_reversible(self):
        raw = r.pinned(r.BASE, r.BASE_SHA)
        derived = r.derive(raw)
        self.assertEqual(derived.replace(r.NEW, r.OLD, 1), raw)
        before, after = ast.parse(raw), ast.parse(derived)
        differences = [getattr(a, 'name', None) for a, b in zip(before.body, after.body)
                       if ast.dump(a) != ast.dump(b)]
        self.assertEqual(len(before.body), len(after.body))
        self.assertEqual(differences, ['verify_packages'])
        with self.assertRaises(ValueError):
            r.derive(raw + b'\n')

    def test_wrong_mpi_outputs_rejected(self):
        module = driver(True)
        actual = module.subprocess.check_output
        frozen = json.loads(r.pinned(r.CONTRACT, r.CONTRACT_SHA))
        for output in ('mpicc: Open MPI 4.1.2 (Language: C)',
                       '/usr/local/bin/mpicc: Open MPI 4.1.2 (Language: C)',
                       '/usr/bin/mpif90: Open MPI 4.1.2 (Language: C)',
                       '/usr/bin/mpicc: Open MPI 4.1.3 (Language: C)',
                       '/usr/bin/mpicc: Open MPI 4.1.2 (Language: Fortran)',
                       '/usr/bin/mpicc: Open MPI 4.1.2 (Language: C) extra',
                       'extra\n/usr/bin/mpicc: Open MPI 4.1.2 (Language: C)'):
            with self.subTest(output=output):
                def injected(argv, **kwargs):
                    return output if argv == ['/usr/bin/mpicc', '--showme:version'] else actual(argv, **kwargs)
                with mock.patch.object(module.subprocess, 'check_output', side_effect=injected):
                    with self.assertRaisesRegex(ValueError, 'openmpi_showme_version'):
                        module.verify_packages(frozen)

    def test_contract_drift_rejected(self):
        module = driver(True)
        frozen = json.loads(r.pinned(r.CONTRACT, r.CONTRACT_SHA))
        frozen['software']['toolchain']['openmpi_showme_version'] = 'mpicc: Open MPI 4.1.3 (Language: C)'
        with self.assertRaisesRegex(ValueError, 'comparison contract differs'):
            module.verify_packages(frozen)

    def test_wrong_path_and_wrapper_still_rejected(self):
        module = driver(True)
        frozen = json.loads(r.pinned(r.CONTRACT, r.CONTRACT_SHA))
        frozen['software']['toolchain']['executables']['mpicc']['path'] = '/usr/local/bin/mpicc'
        with self.assertRaises((ValueError, FileNotFoundError)):
            module.verify_packages(frozen)
        frozen = json.loads(r.pinned(r.CONTRACT, r.CONTRACT_SHA))
        actual = module.subprocess.check_output
        def injected(argv, **kwargs):
            return 'clang' if argv == ['/usr/bin/mpicc', '--showme:command'] else actual(argv, **kwargs)
        with mock.patch.object(module.subprocess, 'check_output', side_effect=injected):
            with self.assertRaisesRegex(ValueError, 'wrapper compiler expansion mismatch'):
                module.verify_packages(frozen)

    def test_readonly_cli_rejects_build(self):
        result = subprocess.run([sys.executable, '-I', '-S', '-B', str(PATH), 'build'], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'only read-only', result.stderr)

    def test_no_capability_means_no_build(self):
        module = driver(True)
        with self.assertRaisesRegex(RuntimeError, 'consumed budget capability'):
            module.build_sources(json.loads(r.pinned(r.CONTRACT, r.CONTRACT_SHA)))

    def test_pinned_rejects_links_and_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'source'
            path.write_bytes(b'base')
            self.assertEqual(r.pinned(path, r.sha(b'base')), b'base')
            with self.assertRaises(ValueError):
                r.pinned(path, r.sha(b'changed'))
            link = path.with_name('link')
            link.symlink_to(path)
            with self.assertRaises(OSError):
                r.pinned(link, r.sha(b'base'))
            link.unlink()
            os.link(path, link)
            with self.assertRaises(ValueError):
                r.pinned(path, r.sha(b'base'))


if __name__ == '__main__':
    unittest.main()
