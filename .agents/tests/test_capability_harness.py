import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("sync_generated_harness", ROOT / ".agents/sync_generated.py")
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class CapabilityHarnessTests(unittest.TestCase):
    def test_canonical_harnesses_match_owned_package_contracts(self):
        payloads = json.loads((ROOT / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))
        config = json.loads((ROOT / ".agents/plugins/sources.json").read_text(encoding="utf-8"))
        for package in payloads["publicPlugins"]:
            with self.subTest(package=package):
                source = ROOT / f".agents/plugins/manifests/harness/{package}.json"
                harness = json.loads(source.read_text(encoding="utf-8"))
                self.assertEqual(harness["schema_version"], 1)
                self.assertEqual(harness["plugin"], f"tj-agents/{package}")
                requires = harness["requires"]
                self.assertEqual(requires["marketplaces"], [{"id": "tj-agents", "repository": "tj-agents/marketplace"}])
                dependencies = payloads["dependencies"].get(package, [])
                self.assertEqual(requires["plugins"], [f"tj-agents/{name}" for name in [package, *dependencies]])
                self.assertEqual(requires["permissions"], {"claude_allow": [], "codex_prefix_rules": []})
                expected_hooks = [{"path": "hooks/session_context.py", "hosts": ["claude", "codex"]}] if package in payloads["hooks"] else []
                self.assertEqual(requires["hooks"], expected_hooks)
                for hook in requires["hooks"]:
                    self.assertTrue((ROOT / f"plugins/{package}" / hook["path"]).is_file())
                    for host in hook["hosts"]:
                        self.assertIn("session_context.py", (ROOT / f"plugins/{package}/hooks/{host}.json").read_text(encoding="utf-8"))
                roots = harness["source_roots"]
                self.assertEqual(len(roots), len(set(roots)))
                for relative in roots:
                    self.assertTrue((ROOT / relative).exists(), relative)
                    self.assertNotIn("..", Path(relative).parts)
                for scope in config["scopes"]:
                    if scope["plugin"] == package:
                        self.assertIn(scope["root"], roots)
                for resource in config["resources"]:
                    if package in resource["plugins"]:
                        self.assertTrue(any(resource["source"] == item or resource["source"].startswith(item + "/") for item in roots))
                if package != "cpp":
                    self.assertIn(".agents/gen_skill_routes.py", roots)

    def test_generator_ships_every_authored_harness(self):
        output, _ = SYNC.build(ROOT)
        payloads = json.loads((ROOT / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))
        for package in payloads["payloads"]:
            with self.subTest(package=package):
                relative = f"plugins/{package}/harness.json"
                source = ROOT / f".agents/plugins/manifests/harness/{package}.json"
                self.assertEqual(output[relative], source.read_bytes())
                self.assertEqual((ROOT / relative).read_bytes(), source.read_bytes())

    def test_generator_rejects_a_non_tj_agents_harness_identity(self):
        payloads = SYNC.load(ROOT / ".agents/plugins/payloads.json")
        source = ROOT / ".agents/plugins/manifests/harness/gpp.json"
        canonical = json.loads(source.read_text(encoding="utf-8"))
        mutations = (
            (lambda harness: harness.update({"plugin": "other/gpp"}), "plugin must be tj-agents/gpp"),
            (lambda harness: harness["requires"].update({"marketplaces": [{"id": "other", "repository": "tj-agents/cpp"}]}), "requires.marketplaces"),
            (lambda harness: harness["requires"]["marketplaces"].append({"id": "other", "repository": "tj-agents/cpp"}), "requires.marketplaces"),
            (lambda harness: harness["requires"].update({"plugins": ["tj-agents/gpp", "other/cpp"]}), "requires.plugins"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "gpp.json"
            for mutate, message in mutations:
                harness = json.loads(json.dumps(canonical))
                mutate(harness)
                target.write_text(json.dumps(harness), encoding="utf-8")
                with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                    SYNC.harness_body(target, "gpp", payloads)


if __name__ == "__main__":
    unittest.main()
