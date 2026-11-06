"""Safety checks run only inside temporary directories; no live cleanup."""
import contextlib
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

import disk_cleanup as cleanup


class CleanupSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home_dir = Path(self.temp.name).resolve()
        self.addCleanup(self.temp.cleanup)

    def file(self, relative, content='keep'):
        path = self.home_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def remove(self, key, path, authorized=False, processes=lambda: []):
        return cleanup.remove_target(self.home_dir, key, path, authorized, processes)

    def test_npm_removal_preserves_npx_and_work(self):
        cache = self.file('.npm/_cacache/content-v2/package', 'download').parents[1]
        npx = self.file('.npm/_npx/runtime/index.js')
        work = self.file('Documents/project/source.py')
        self.assertEqual(self.remove('npm-downloads', cache), 'removed')
        self.assertFalse(cache.exists())
        self.assertEqual(npx.read_text(), 'keep')
        self.assertEqual(work.read_text(), 'keep')

    def test_pip_removal_preserves_local_wheels(self):
        cache = self.file('Library/Caches/pip/http-v2/http-response').parent
        wheel = self.file('Library/Caches/pip/wheels/custom.whl')
        self.remove('pip-downloads', cache)
        self.assertFalse(cache.exists())
        self.assertEqual(wheel.read_text(), 'keep')

    def test_model_authorization_and_preservation(self):
        model = self.file('.lmstudio/models/vendor/model.gguf')
        root = model.parents[1]
        root.chmod(0o750)
        records = [self.file('.lmstudio/conversations/chat.json'),
                   self.file('.lmstudio/extensions/backends/runtime'),
                   self.file('.lmstudio/credentials/key')]
        with self.assertRaises(ValueError):
            self.remove('lmstudio-models', root)
        self.assertTrue(model.exists())
        self.remove('lmstudio-models', root, authorized=True)
        self.assertEqual(list(root.iterdir()), [])
        self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o750)
        self.assertTrue(all(p.read_text() == 'keep' for p in records))

    def test_ollama_preserves_keys_and_history(self):
        blob = self.file('.ollama/models/blobs/weights')
        manifest = self.file('.ollama/models/manifests/custom/model')
        key = self.file('.ollama/id_ed25519')
        history = self.file('.ollama/history')
        root = self.home_dir / '.ollama/models'
        self.remove('ollama-models', root, authorized=True)
        self.assertEqual(list(root.iterdir()), [])
        self.assertFalse(blob.exists())
        self.assertFalse(manifest.exists())
        self.assertEqual(key.read_text(), 'keep')
        self.assertEqual(history.read_text(), 'keep')

    def test_refuse_outside_allowlist(self):
        work = self.file('Documents/important.txt')
        with self.assertRaises(ValueError):
            self.remove('npm-downloads', work.parent)
        self.assertTrue(work.exists())

    def test_refuse_target_and_internal_symlink(self):
        work = self.file('Documents/important.txt')
        cache = self.home_dir / '.npm/_cacache'
        cache.parent.mkdir()
        cache.symlink_to(work.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.remove('npm-downloads', cache)
        cache.unlink()
        cache.mkdir()
        (cache / 'linked-work').symlink_to(work.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.remove('npm-downloads', cache)
        self.assertEqual(work.read_text(), 'keep')

    def test_refuse_mount(self):
        cache = self.file('.npm/_cacache/file').parent
        with patch.object(cleanup.os.path, 'ismount', return_value=True):
            with self.assertRaises(ValueError):
                self.remove('npm-downloads', cache)
        self.assertTrue(cache.exists())

    def test_active_process_and_start_during_check(self):
        cache = self.file('.npm/_cacache/file').parent
        running = [{'pid': 111, 'tool': 'npm'}]
        with self.assertRaises(ValueError):
            self.remove('npm-downloads', cache, processes=lambda: running)
        sequence = iter([[], running])
        with self.assertRaises(ValueError):
            self.remove('npm-downloads', cache, processes=lambda: next(sequence))
        self.assertTrue((cache / 'file').exists())

    def test_process_detection_without_secret_output(self):
        for command, tool in [
            ('/opt/bin/node /opt/lib/npm/bin/npm-cli.js install', 'npm'),
            ('/opt/bin/python3 -m pip install pkg --password PRIVATE', 'pip'),
            ('/Applications/LM Studio.app/Contents/MacOS/LM Studio', 'lmstudio'),
            ('/opt/bin/ollama serve', 'ollama'),
            ('/bin/uv pip install pkg', 'pip'),
        ]:
            self.assertEqual(cleanup.identify_process(command), tool)
        self.assertIsNone(cleanup.identify_process('/bin/python disk_cleanup.py'))

    def test_default_scan_does_not_delete(self):
        cache = self.file('.npm/_cacache/file', 'download')
        model = self.file('.ollama/models/blobs/file', 'weights')
        with patch.object(cleanup.Path, 'home', return_value=self.home_dir), \
             patch.object(sys, 'argv', ['disk_cleanup.py', '--skip-home-inventory']), \
             patch.object(cleanup, 'active_tools', return_value=[]), \
             patch.object(cleanup.platform, 'system', return_value='Darwin'), \
             patch.object(cleanup.shutil, 'disk_usage', return_value=shutil_usage()), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cleanup.main(), 0)
        self.assertEqual(cache.read_text(), 'download')
        self.assertEqual(model.read_text(), 'weights')
        audit = next((self.home_dir / 'disk-cleanup-reports').glob('*/audit.json'))
        self.assertEqual(json.loads(audit.read_text())['mode'], 'scan')


def shutil_usage():
    from collections import namedtuple
    return namedtuple('DiskUsage', 'total used free')(100000, 50000, 50000)


if __name__ == '__main__':
    unittest.main()
