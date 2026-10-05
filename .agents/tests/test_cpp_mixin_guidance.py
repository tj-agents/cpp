import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / ".agents/base/convention/mixins/SKILL.md"
GENERATED = (
    ROOT / "plugins/cpp/skills/mixins/SKILL.md",
    ROOT / "plugins/base/skills/mixins/SKILL.md",
    ROOT / "plugins/cpp-standards/skills/mixins/SKILL.md",
)
AUTHORED_SCOPE_ROOTS = (
    ROOT / ".agents/base",
    ROOT / ".agents/gpp",
    ROOT / ".agents/msvc",
    ROOT / ".agents/win32",
)
FORBIDDEN_OWNERSHIP_MARKERS = (
    "## Compose behavior deliberately",
    "### Behavior-provider names",
    "Use a transparent `struct` when the provider is stateless",
    "struct FileDroppable",
    "first-match-wins",
    "ACME_DETAIL_EVENT",
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
        for scope_root in AUTHORED_SCOPE_ROOTS:
            for path in scope_root.glob("*/*/SKILL.md"):
                if path == CANONICAL:
                    continue
                guidance = path.read_text(encoding="utf-8")
                with self.subTest(path=path.relative_to(ROOT).as_posix()):
                    for marker in FORBIDDEN_OWNERSHIP_MARKERS:
                        self.assertNotIn(marker, guidance)

        win32_style = (ROOT / ".agents/win32/convention/style/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Load `cpp:mixins`", win32_style)
        self.assertNotIn("historically CRTP", win32_style)
        self.assertNotIn("composed mixins", win32_style)

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

    def test_examples_are_structurally_complete_everywhere(self) -> None:
        for path in (CANONICAL, *GENERATED):
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                guidance = path.read_text(encoding="utf-8")
                blocks = re.findall(r"```(?:cpp|text)\n(.*?)```", guidance, re.DOTALL)

                provider = next(block for block in blocks if "struct FileDroppable" in block)
                self.assertIn("static_cast<Host&>(*this).on_file_drop(drop->path)", provider)

                dispatch = next(block for block in blocks if "class Editor" in block)
                self.assertIn("return FileDroppable<Editor>::try_handle(event) ||", dispatch)
                self.assertIn("CommandRouter<Editor>::try_handle(event)", dispatch)

                fragment = next(block for block in blocks if "#ifndef ACME_DETAIL_EVENT" in block)
                self.assertIn('#error "Define ACME_DETAIL_EVENT before including this internal fragment"', fragment)
                self.assertIn("ACME_DETAIL_EVENT(file_drop)", fragment)
                self.assertIn("ACME_DETAIL_EVENT(command)", fragment)

                public_header = next(block for block in blocks if "enum class EventKind" in block)
                self.assertEqual(2, public_header.count(DETAIL_INCLUDE))
                normalized_header = " ".join(public_header.split())
                for expansion in MACRO_EXPANSIONS:
                    self.assertIn(expansion, normalized_header)

                leakage = next(block for block in blocks if "event_kind.hpp leaked" in block)
                self.assertIn("#include <acme/event_kind.hpp>", leakage)
                self.assertIn("#if defined(ACME_DETAIL_EVENT)", leakage)
                self.assertIn("int main() {}", leakage)


if __name__ == "__main__":
    unittest.main()
