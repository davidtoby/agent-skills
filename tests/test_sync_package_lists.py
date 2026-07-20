import tempfile
import unittest
from pathlib import Path

from scripts import sync_package_lists


class SyncPackageListsTests(unittest.TestCase):
    def make_docs(self, root: Path) -> tuple[Path, Path, Path]:
        packages_dir = root / 'packages'
        packages_dir.mkdir()
        for name in ['b.skill', 'a.skill']:
            (packages_dir / name).write_text('', encoding='utf-8')

        readme = root / 'README.md'
        readme.write_text(
            '\n'.join(
                [
                    'before',
                    sync_package_lists.PACKAGE_MARKER_START,
                    '- stale',
                    sync_package_lists.PACKAGE_MARKER_END,
                    'after',
                    '',
                ]
            ),
            encoding='utf-8',
        )

        skills_readme = root / 'skills_README.md'
        skills_readme.write_text(
            '\n'.join(
                [
                    'before',
                    sync_package_lists.PACKAGE_MARKER_START,
                    '- stale',
                    sync_package_lists.PACKAGE_MARKER_END,
                    'after',
                    '',
                ]
            ),
            encoding='utf-8',
        )
        return packages_dir, readme, skills_readme

    def test_check_only_fails_when_package_lists_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packages_dir, readme, skills_readme = self.make_docs(root)

            with self.assertRaises(SystemExit) as exc:
                sync_package_lists.sync_package_lists(
                    packages_dir=packages_dir,
                    readme=readme,
                    skills_readme=skills_readme,
                    check_only=True,
                )

            self.assertEqual(exc.exception.code, 1)
            self.assertIn('- stale', readme.read_text(encoding='utf-8'))
            self.assertIn('- stale', skills_readme.read_text(encoding='utf-8'))

    def test_check_only_passes_when_package_lists_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packages_dir, readme, skills_readme = self.make_docs(root)

            sync_package_lists.sync_package_lists(
                packages_dir=packages_dir,
                readme=readme,
                skills_readme=skills_readme,
                check_only=False,
            )

            sync_package_lists.sync_package_lists(
                packages_dir=packages_dir,
                readme=readme,
                skills_readme=skills_readme,
                check_only=True,
            )

    def test_package_names_sort_by_skill_stem_not_extension_punctuation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packages_dir = Path(tmp)
            for name in ['lark-vc.skill', 'lark-vc-agent.skill']:
                (packages_dir / name).write_text('', encoding='utf-8')
            self.assertEqual(
                sync_package_lists.package_names(packages_dir),
                ['lark-vc.skill', 'lark-vc-agent.skill'],
            )

    def test_parse_args_supports_check_only_flag(self) -> None:
        args = sync_package_lists.parse_args(['--check-only'])
        self.assertTrue(args.check_only)


if __name__ == '__main__':
    unittest.main()
