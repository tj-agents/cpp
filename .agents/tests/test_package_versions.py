import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("sync_generated", ROOT / ".agents/sync_generated.py")
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class PackageVersionTests(unittest.TestCase):
    def test_every_package_version_names_exactly_the_content_it_ships(self) -> None:
        recorded = json.loads((ROOT / SYNC.PACKAGE_VERSIONS).read_text(encoding="utf-8"))
        payloads = json.loads((ROOT / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))
        self.assertEqual(set(payloads["payloads"]), set(recorded))
        for package in sorted(payloads["payloads"]):
            version, digest = SYNC.package_state(ROOT, package)
            history = recorded[package]
            self.assertIn(
                version, history,
                f"{package} {version} is unrecorded: run `python .agents/sync_generated.py --record-package-versions`",
            )
            self.assertEqual(
                history[version], digest,
                f"{package} content changed without a version bump from {version}; bump both host manifests, "
                "regenerate, then record the new version",
            )


if __name__ == "__main__":
    unittest.main()
