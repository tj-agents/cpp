from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_GUIDANCE = (
    "normal single-product rule of thumb",
    "The single-product layout is a rule of thumb, not a reason to flatten a multi-product repository.",
    "`client/`, `driver/`, and `shared/`",
    "Apply the app/library/test structure within each owning product",
    "code moves to `shared/` only when multiple products genuinely consume it",
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class CppStructureTests(unittest.TestCase):
    def test_canonical_guidance_preserves_meaningful_product_boundaries(self) -> None:
        canonical = normalized(ROOT / ".agents/base/convention/structure/SKILL.md")
        for guidance in REQUIRED_GUIDANCE:
            self.assertIn(guidance, canonical)

    def test_generated_packages_preserve_meaningful_product_boundaries(self) -> None:
        for package, capability in (("cpp", "structure"), ("base", "cpp-structure"), ("cpp-standards", "cpp-structure")):
            generated = normalized(ROOT / f"plugins/{package}/skills/{capability}/SKILL.md")
            with self.subTest(package=package):
                for guidance in REQUIRED_GUIDANCE:
                    self.assertIn(guidance, generated)


if __name__ == "__main__":
    unittest.main()
