import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("versionless_sync", ROOT / ".agents/sync_generated.py")
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class VersionlessPackageTests(unittest.TestCase):
    def test_every_current_package_omits_release_versions(self):
        config = SYNC.load(ROOT / ".agents/plugins/sources.json")
        for package in config["packages"]:
            for host, source in config["host_manifest_roots"].items():
                with self.subTest(package=package, host=host):
                    authored = SYNC.load(ROOT / source / f"{package}.json")
                    packaged = SYNC.load(ROOT / "plugins" / package / f".{host}-plugin/plugin.json")
                    self.assertNotIn("version", authored)
                    self.assertNotIn("version", packaged)
                    self.assertEqual(authored, packaged)

    def test_generator_rejects_a_reintroduced_version_on_either_host(self):
        config = SYNC.load(ROOT / ".agents/plugins/sources.json")
        payloads = SYNC.load(ROOT / ".agents/plugins/payloads.json")
        skills = SYNC.discover(ROOT, config)
        original = SYNC.load
        for host, source in config["host_manifest_roots"].items():
            target = ROOT / source / "cpp.json"
            def load(path):
                document = original(path)
                return dict(document, version="99.0.0") if path == target else document
            with self.subTest(host=host), mock.patch.object(SYNC, "load", side_effect=load):
                with self.assertRaisesRegex(ValueError, "must omit version"):
                    SYNC.validate(ROOT, config, payloads, skills)


if __name__ == "__main__":
    unittest.main()
