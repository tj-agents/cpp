import importlib.util
import json
import re
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PAYLOADS = ROOT / ".agents" / "plugins" / "payloads.json"
SKILL_CONTRACT = ROOT / ".agents" / "plugins" / "skill-contract.json"
GENERATOR = ROOT / ".agents" / "gen_skill_routes.py"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_generator():
    spec = importlib.util.spec_from_file_location("gen_skill_routes", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarketplaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.marketplace = read_json(MARKETPLACE)
        cls.payloads = read_json(PAYLOADS)
        cls.contract = read_json(SKILL_CONTRACT)
        cls.generator = load_generator()

    def test_public_plugins_are_the_three_layers_in_order(self) -> None:
        self.assertEqual(["base", "windows", "gcc"], self.payloads["publicPlugins"])
        names = [plugin["name"] for plugin in self.marketplace["plugins"]]
        self.assertEqual(self.payloads["publicPlugins"], names[:3])

    def test_every_marketplace_entry_has_a_matching_manifest_and_payload(self) -> None:
        for entry in self.marketplace["plugins"]:
            name = entry["name"]
            manifest_path = ROOT / entry["source"]["path"] / ".codex-plugin" / "plugin.json"
            manifest = read_json(manifest_path)
            self.assertEqual(name, manifest["name"])
            self.assertIn(name, self.payloads["payloads"])

    def test_layer_dependencies_exist_and_are_acyclic(self) -> None:
        names = set(self.payloads["payloads"])
        dependencies = self.payloads["dependencies"]
        self.assertEqual(["base"], dependencies["windows"])
        self.assertEqual(["base"], dependencies["gcc"])
        for plugin, required in dependencies.items():
            self.assertIn(plugin, names)
            self.assertNotIn(plugin, required)
            self.assertTrue(set(required) <= names)

        def visit(plugin: str, active: set[str], complete: set[str]) -> None:
            if plugin in active:
                self.fail(f"plugin dependency cycle includes {plugin}")
            if plugin in complete:
                return
            active.add(plugin)
            for dependency in dependencies.get(plugin, []):
                visit(dependency, active, complete)
            active.remove(plugin)
            complete.add(plugin)

        complete: set[str] = set()
        for name in names:
            visit(name, set(), complete)

    def test_compatibility_aliases_are_time_bounded_and_not_public(self) -> None:
        public = set(self.payloads["publicPlugins"])
        aliases = self.payloads["compatibilityAliases"]
        self.assertEqual({"cpp-standards", "gpp-standards"}, set(aliases))
        for name, alias in aliases.items():
            self.assertNotIn(name, public)
            self.assertIn(alias["replacedBy"], public)
            self.assertGreater(date.fromisoformat(alias["removeAfter"]), date(2026, 9, 13))

    def test_generated_routes_reference_real_skill_contracts(self) -> None:
        local_skills = {
            path.parent.name
            for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md")
        }
        public_domains = {
            plugin: set(self.payloads["payloads"][plugin])
            for plugin in self.payloads["publicPlugins"]
        }
        skill_domains = {}
        for skill_file in (ROOT / ".agents" / "skills").glob("*/SKILL.md"):
            text = skill_file.read_text(encoding="utf-8")
            match = re.search(r"`standards/([^/]+)/", text)
            self.assertIsNotNone(match, skill_file)
            skill_domains[skill_file.parent.name] = match.group(1)

        external = self.contract["externalPlugins"]
        for kind in self.generator.CANONICAL_KINDS:
            for route in self.generator.routes(kind)["routes"]:
                for identifier in route.get("skills", []):
                    plugin, skill = identifier.split(":", 1)
                    if plugin in public_domains:
                        self.assertIn(skill, local_skills, identifier)
                        self.assertIn(skill_domains[skill], public_domains[plugin], identifier)
                    else:
                        self.assertIn(plugin, external, identifier)
                        self.assertIn(skill, external[plugin]["skills"], identifier)

    def test_canonical_sources_contain_no_retired_plugin_identifiers(self) -> None:
        retired = re.compile(r"cpp-standards|gpp-standards|windows-standards|agent-process:")
        roots = [ROOT / "standards", ROOT / ".agents" / "skills"]
        files = [ROOT / ".agents" / "gen_skill_routes.py", ROOT / ".agents" / "hooks" / "session_context.py"]
        for source_root in roots:
            files.extend(source_root.rglob("*.md"))
        offenders = []
        for path in files:
            if retired.search(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
