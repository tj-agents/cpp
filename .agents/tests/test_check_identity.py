import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("check_identity", ROOT / ".github/scripts/check_identity.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
PACKAGES = {"cpp", "gpp", "msvc", "win32"}
CANONICAL_HARNESS = {
    "schema_version": 1,
    "plugin": "tj-agents/gpp",
    "requires": {
        "marketplaces": [{"id": "tj-agents", "repository": "tj-agents/marketplace"}],
        "plugins": ["tj-agents/gpp", "tj-agents/cpp"],
    },
}


class IdentityCheckTests(unittest.TestCase):
    def check(self, files: dict[str, str]) -> list[str]:
        base = {
            ".claude-plugin/marketplace.json": json.dumps({"name": "tj-agents"}),
            ".agents/plugins/marketplace.json": json.dumps({"name": "tj-agents"}),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative, text in {**base, **files}.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            return CHECK.problems(root, list({**base, **files}), PACKAGES)

    def test_repository_has_only_tj_agents_identities(self):
        self.assertEqual([], CHECK.problems(ROOT, CHECK.tracked_files(ROOT), PACKAGES))

    def test_canonical_fixture_passes(self):
        files = {
            "plugins/gpp/harness.json": json.dumps(CANONICAL_HARNESS),
            "README.md": "Install `gpp@tj-agents`; see actions/checkout@v4 and noreply@anthropic.com.\n",
        }
        self.assertEqual([], self.check(files))

    def test_rejects_a_legacy_marketplace_name(self):
        for host in CHECK.MARKETPLACE_FILES:
            with self.subTest(host=host):
                found = self.check({host: json.dumps({"name": "cpp-agents"})})
                self.assertTrue(any("marketplace name must be tj-agents" in problem for problem in found), found)

    def test_rejects_legacy_harness_identities(self):
        mutations = (
            ({"plugin": "cpp-agents/gpp"}, "plugin must be tj-agents/gpp"),
            ({"requires": {**CANONICAL_HARNESS["requires"], "marketplaces": [{"id": "cpp-agents", "repository": "tj-agents/cpp"}]}}, "requires.marketplaces"),
            ({"requires": {**CANONICAL_HARNESS["requires"], "plugins": ["tj-agents/gpp", "base-agents/base"]}}, "is not a tj-agents/<plugin> identity"),
        )
        for change, message in mutations:
            with self.subTest(message=message):
                found = self.check({".agents/plugins/manifests/harness/gpp.json": json.dumps({**CANONICAL_HARNESS, **change})})
                self.assertTrue(any(message in problem for problem in found), found)

    def test_rejects_legacy_selectors_and_marketplace_names_in_text(self):
        for line in ("Apply cpp@cpp-agents.", "codex plugin add \"$plugin@windows-agents\"", "the cpp-agents marketplace", "install msvc@other"):
            with self.subTest(line=line):
                self.assertNotEqual([], self.check({"AGENTS.md": line + "\n"}))

    def test_rejects_a_non_tj_agents_plugin_dependency(self):
        found = self.check({"plugins/gpp/.claude-plugin/plugin.json": json.dumps({"name": "gpp", "dependencies": ["cpp@other"]})})
        self.assertTrue(any("dependency 'cpp@other'" in problem for problem in found), found)

    def test_historical_records_are_not_scanned(self):
        self.assertEqual([], self.check({"plans/old/PLAN.md": "cpp@cpp-agents\n", "CHANGELOG.md": "cpp-agents\n"}))


if __name__ == "__main__":
    unittest.main()
