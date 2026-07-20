import importlib.util
import tempfile
import unittest
from pathlib import Path
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'rebuild_all_packages.py'
SPEC = importlib.util.spec_from_file_location('rebuild_all_packages', SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f'Unable to load {SCRIPT}')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PackageFallbackTests(unittest.TestCase):
    def test_standard_library_fallback_mirrors_source_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'demo-skill'
            (skill / 'references').mkdir(parents=True)
            (skill / 'SKILL.md').write_text('---\nname: demo-skill\ndescription: "demo"\n---\n\n# Demo\n')
            (skill / 'references' / 'guide.md').write_text('guide\n')

            old_packages = getattr(MODULE, 'PACKAGES_DIR')
            old_script = getattr(MODULE, 'PACKAGE_SCRIPT')
            try:
                packages = root / 'packages'
                packages.mkdir()
                setattr(MODULE, 'PACKAGES_DIR', packages)
                setattr(MODULE, 'PACKAGE_SCRIPT', root / 'missing-package-skill.py')
                getattr(MODULE, 'package_skill')(skill)
            finally:
                setattr(MODULE, 'PACKAGES_DIR', old_packages)
                setattr(MODULE, 'PACKAGE_SCRIPT', old_script)

            package = root / 'packages' / 'demo-skill.skill'
            self.assertTrue(package.exists())
            with zipfile.ZipFile(package) as bundle:
                self.assertEqual(
                    sorted(bundle.namelist()),
                    ['demo-skill/SKILL.md', 'demo-skill/references/guide.md'],
                )
                self.assertEqual(bundle.read('demo-skill/references/guide.md'), b'guide\n')


if __name__ == '__main__':
    unittest.main()
