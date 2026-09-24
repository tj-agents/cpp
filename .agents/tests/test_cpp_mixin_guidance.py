import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / ".agents/base/contract/mixins/SKILL.md"
GENERATED = (
    ROOT / "plugins/cpp/skills/mixins/SKILL.md",
    ROOT / "plugins/base/skills/mixins/SKILL.md",
    ROOT / "plugins/cpp-standards/skills/mixins/SKILL.md",
)
NEIGHBOURING_CAPABILITIES = (
    "domain-design",
    "structure",
    "style",
    "testing",
)
REQUIRED_GUIDANCE = (
    "Mixins are a general C++ composition pattern",
    "not domain-driven design",
    "Use a transparent `struct` when the provider is stateless",
    "first-match-wins",
    "construction and destruction order when several bases own resources",
    "The language mechanism does not automatically require a `mixins/` directory",
    "`detail/` means the declaration has no supported compatibility contract",
    "A macro cannot live in a C++ namespace",
    "overlapping conditions follow the documented first-match rule",
    "only instantiating provider templates",
)
DETAIL_INCLUDE = "#include <acme/detail/event_kinds.inc>"
MACRO_EXPANSIONS = (
    f"#define ACME_DETAIL_EVENT(name) name, {DETAIL_INCLUDE} #undef ACME_DETAIL_EVENT",
    "#define ACME_DETAIL_EVENT(name) case EventKind::name: return #name; "
    f"{DETAIL_INCLUDE} #undef ACME_DETAIL_EVENT",
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class CppMixinGuidanceTests(unittest.TestCase):
    def test_mixins_are_a_standalone_canonical_capability(self) -> None:
        guidance = normalized(CANONICAL)
        self.assertIn("name: mixins", guidance)
        for phrase in REQUIRED_GUIDANCE:
            self.assertIn(phrase, guidance)

    def test_generated_packages_publish_the_standalone_capability(self) -> None:
        for path in GENERATED:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                guidance = normalized(path)
                for phrase in REQUIRED_GUIDANCE:
                    self.assertIn(phrase, guidance)

    def test_mixins_do_not_return_to_unrelated_capabilities(self) -> None:
        for capability in NEIGHBOURING_CAPABILITIES:
            path = ROOT / f".agents/base/contract/{capability}/SKILL.md"
            guidance = path.read_text(encoding="utf-8").casefold()
            with self.subTest(capability=capability):
                self.assertNotRegex(guidance, r"\bmixins?\b")
                self.assertNotIn("filedroppable", guidance)
                self.assertNotIn("acme_detail_event", guidance)

    def test_repository_instructions_guard_capability_ownership(self) -> None:
        agents = normalized(ROOT / "AGENTS.md")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").strip()
        self.assertIn("Capability ownership must match the subject", agents)
        self.assertIn("belong to `cpp:mixins`, never `cpp:domain-design`", agents)
        self.assertEqual("@AGENTS.md", claude)

    def test_discovery_and_compatibility_maps_expose_mixins(self) -> None:
        sources = json.loads((ROOT / ".agents/plugins/sources.json").read_text(encoding="utf-8"))
        payloads = json.loads((ROOT / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))
        self.assertEqual("cpp-mixins", sources["hostAdapterNames"]["cpp:mixins"])
        for package, identifier in (("base", "base:mixins"), ("cpp-standards", "cpp-standards:mixins")):
            with self.subTest(package=package):
                self.assertEqual("mixins", sources["packages"][package]["skillNames"]["cpp:mixins"])
                self.assertEqual(identifier, sources["packages"][package]["identifierRewrites"]["cpp:mixins"])
                self.assertEqual("cpp:mixins", payloads["compatibilityAliases"][package]["skillAliases"]["mixins"])

    def test_macro_example_is_repeatable_and_contained_everywhere(self) -> None:
        for path in (CANONICAL, *GENERATED):
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                guidance = normalized(path)
                self.assertEqual(2, guidance.count(DETAIL_INCLUDE))
                for expansion in MACRO_EXPANSIONS:
                    self.assertIn(expansion, guidance)


if __name__ == "__main__":
    unittest.main()
