import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CapabilityHarnessTests(unittest.TestCase):
    def test_both_catalogs_publish_shared_identity(self) -> None:
        for relative in (
            ".claude-plugin/marketplace.json",
            ".agents/plugins/marketplace.json",
        ):
            self.assertEqual(
                "tj-agents", json.loads((ROOT / relative).read_text())["name"]
            )

    def test_packages_ship_declared_roots_and_effective_requirements(self) -> None:
        for plugin in ("cpp", "gpp", "msvc", "win32"):
            source = json.loads(
                (ROOT / f".agents/plugins/manifests/harness/{plugin}.json").read_text()
            )
            package = ROOT / f"plugins/{plugin}"
            shipped = json.loads((package / "harness.json").read_text())
            self.assertEqual(f"tj-agents/{plugin}", shipped["plugin"])
            self.assertEqual(source["source_roots"], shipped["source_roots"])
            expected = {
                f"tj-agents/{plugin}",
                "tj-agents/base",
                "tj-agents/engineering",
            }
            if plugin != "cpp":
                expected.add("tj-agents/cpp")
            self.assertEqual(expected, set(shipped["requires"]["plugins"]))
            self.assertEqual(
                {"claude_allow": [], "codex_prefix_rules": []},
                shipped["requires"]["permissions"],
            )
            for relative in source["source_roots"]:
                originals = {
                    p.relative_to(ROOT / relative): p.read_bytes()
                    for p in (ROOT / relative).rglob("*")
                    if p.is_file()
                }
                for path, content in originals.items():
                    self.assertEqual(content, (package / relative / path).read_bytes())
            for hook in shipped["requires"]["hooks"]:
                self.assertTrue((package / hook["path"]).is_file())
