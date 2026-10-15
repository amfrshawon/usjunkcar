import importlib.util
from pathlib import Path
import subprocess
import tarfile
import unittest

spec=importlib.util.spec_from_file_location('receiver',Path(__file__).resolve().parents[2]/'infra/vps/receive-release.py')
receiver=importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)

class ReleaseSafety(unittest.TestCase):
    def test_static_preview_is_dev_only(self):
        sha='a'*40
        receiver.validate_manifest({'commit':sha,'branch':'dev','kind':'static-preview'},sha,'dev')
        with self.assertRaises(ValueError): receiver.validate_manifest({'commit':sha,'branch':'main','kind':'static-preview'},sha,'main')
    def test_rejects_parent_path(self):
        with self.assertRaises(ValueError): receiver.validate_members([tarfile.TarInfo('../outside')])
    def test_rejects_absolute_path(self):
        with self.assertRaises(ValueError): receiver.validate_members([tarfile.TarInfo('/etc/passwd')])
    def test_rejects_symlink(self):
        item=tarfile.TarInfo('link');item.type=tarfile.SYMTYPE;item.linkname='/etc/passwd'
        with self.assertRaises(ValueError): receiver.validate_members([item])
    def test_rejects_environment_secrets(self):
        with self.assertRaises(ValueError): receiver.validate_members([tarfile.TarInfo('apps/web/.env.production')])
    def test_rejects_oversized_archive(self):
        item=tarfile.TarInfo('large');item.size=receiver.MAX_BYTES+1
        with self.assertRaises(ValueError): receiver.validate_members([item])
    def test_accepts_regular_standalone_file(self):
        receiver.validate_members([tarfile.TarInfo('apps/web/server.js')])
    def test_current_disabled_configuration(self):
        subprocess.run(['node','scripts/check-infrastructure.mjs'],check=True)
