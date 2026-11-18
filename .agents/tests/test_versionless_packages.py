import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "versionless_sync", ROOT / ".agents/sync_generated.py"
)
assert SPEC is not None and SPEC.loader is not None
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class VersionlessPackageTests(unittest.TestCase):
    def test_authored_and_packaged_manifests_omit_release_versions(self) -> None:
        for package in ("cpp", "gpp", "msvc", "win32"):
            for host in ("codex", "claude"):
                authored = json.loads(
                    (
                        ROOT / f".agents/plugins/manifests/{host}/{package}.json"
                    ).read_text()
                )
                packaged = json.loads(
                    (ROOT / f"plugins/{package}/.{host}-plugin/plugin.json").read_text()
                )
                self.assertNotIn("version", authored)
                self.assertNotIn("version", packaged)
                for field in ("name", "description", "repository", "skills", "hooks"):
                    self.assertEqual(authored.get(field), packaged.get(field))

    def test_generator_rejects_a_reintroduced_version_on_either_host(self) -> None:
        original = SYNC.load
        for host in ("claude", "codex"):
            target = ROOT / f".agents/plugins/manifests/{host}/cpp.json"

            def load(path: Path, target: Path = target) -> object:
                document = original(path)
                return dict(document, version="99.0.0") if path == target else document

            with (
                self.subTest(host=host),
                mock.patch.object(SYNC, "load", side_effect=load),
                self.assertRaisesRegex(ValueError, "must omit version"),
            ):
                SYNC.build(ROOT)
