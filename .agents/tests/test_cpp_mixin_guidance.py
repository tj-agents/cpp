from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_GUIDANCE = {
    "domain-design": (
        "Use a transparent `struct` when the provider is stateless",
        "first-match-wins",
        "construction and destruction order when several bases own resources",
    ),
    "structure": (
        "A language mechanism such as a mixin",
        "`detail/` means the declaration has no supported compatibility contract",
        "Keep paths independent from C++ namespaces",
    ),
    "style": (
        "such as `FileDroppable`",
        "A macro cannot live in a C++ namespace",
        "`#undef` it before the public header finishes",
        "The `.inc` file deliberately has no `#pragma once`",
    ),
    "testing": (
        "#if defined(ACME_DETAIL_EVENT)",
        "overlapping conditions follow the documented first-match rule",
        "only instantiating the provider templates",
    ),
}
PACKAGE_CAPABILITIES = {
    "cpp": {
        "domain-design": "domain-design",
        "structure": "structure",
        "style": "style",
        "testing": "testing",
    },
    "base": {
        "domain-design": "domain-design",
        "structure": "cpp-structure",
        "style": "cpp-style",
        "testing": "cpp-testing",
    },
    "cpp-standards": {
        "domain-design": "domain-design",
        "structure": "cpp-structure",
        "style": "cpp-style",
        "testing": "cpp-testing",
    },
}
DETAIL_INCLUDE = "#include <acme/detail/event_kinds.inc>"
MACRO_EXPANSIONS = (
    f"#define ACME_DETAIL_EVENT(name) name, {DETAIL_INCLUDE} #undef ACME_DETAIL_EVENT",
    "#define ACME_DETAIL_EVENT(name) case EventKind::name: return #name; "
    f"{DETAIL_INCLUDE} #undef ACME_DETAIL_EVENT",
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class CppMixinGuidanceTests(unittest.TestCase):
    def test_canonical_guidance_keeps_each_decision_with_its_owner(self) -> None:
        for capability, guidance in REQUIRED_GUIDANCE.items():
            canonical = normalized(ROOT / f".agents/base/contract/{capability}/SKILL.md")
            with self.subTest(capability=capability):
                for phrase in guidance:
                    self.assertIn(phrase, canonical)

    def test_generated_packages_preserve_mixin_guidance(self) -> None:
        for package, capabilities in PACKAGE_CAPABILITIES.items():
            for owner, capability in capabilities.items():
                generated = normalized(ROOT / f"plugins/{package}/skills/{capability}/SKILL.md")
                with self.subTest(package=package, capability=capability):
                    for phrase in REQUIRED_GUIDANCE[owner]:
                        self.assertIn(phrase, generated)

    def test_canonical_macro_example_is_repeatable_and_contained(self) -> None:
        self.assert_macro_example(ROOT / ".agents/base/contract/style/SKILL.md")

    def test_generated_macro_examples_are_repeatable_and_contained(self) -> None:
        for package, capabilities in PACKAGE_CAPABILITIES.items():
            with self.subTest(package=package):
                self.assert_macro_example(
                    ROOT / f"plugins/{package}/skills/{capabilities['style']}/SKILL.md"
                )

    def assert_macro_example(self, path: Path) -> None:
        guidance = normalized(path)
        self.assertEqual(2, guidance.count(DETAIL_INCLUDE))
        for expansion in MACRO_EXPANSIONS:
            self.assertIn(expansion, guidance)


if __name__ == "__main__":
    unittest.main()
