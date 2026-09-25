import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / ".agents/gen_skill_routes.py"


class RouteCliTests(unittest.TestCase):
    def generated(self, *arguments: str) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = subprocess.run([sys.executable, str(GENERATOR), *arguments, "--into", str(root)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            return json.loads((root / ".agents/skill-routes.json").read_text(encoding="utf-8"))

    @staticmethod
    def matching_skills(declaration: dict, path: str) -> set[str]:
        return {skill for route in declaration["routes"] if re.search(route["path"], path) for skill in route["skills"]}

    def test_canonical_profiles_resolve_installed_skills(self) -> None:
        for toolchain in (None, "gpp", "msvc"):
            for apis in ([], ["win32"]):
                with self.subTest(toolchain=toolchain, apis=apis):
                    arguments = ["--toolchain", toolchain] if toolchain else []
                    for api in apis:
                        arguments.extend(["--api", api])
                    declaration = self.generated(*arguments)
                    self.assertEqual({"toolchain": toolchain, "apis": apis}, declaration["profile"])
                    self.assertEqual(["cpp", *([toolchain] if toolchain else []), *apis], declaration["layers"])
                    expected = {"cpp:style", "cpp:domain-design", "cpp:mixins"}
                    if toolchain:
                        expected.add(f"{toolchain}:toolchain")
                    if apis:
                        expected.update({"win32:style", "win32:overview"})
                    for path in ("src/main.cpp", "libs/core/include/core/model.hpp"):
                        self.assertEqual(expected, self.matching_skills(declaration, path))
                    self.assertEqual(expected | {"cpp:testing"}, self.matching_skills(declaration, "tests/core_test.cpp"))
                    for route in declaration["routes"]:
                        for identifier in route["skills"]:
                            package, capability = identifier.split(":")
                            self.assertIn(package, declaration["layers"])
                            self.assertNotRegex(capability, r"^(?:cpp|gpp|msvc|win32|windows)-")
                            self.assertTrue((ROOT / "plugins" / package / "skills" / capability / "SKILL.md").is_file(), identifier)

    def test_legacy_options_emit_canonical_routes(self) -> None:
        cases = (
            (("--kind", "generic"), None, []),
            (("--kind", "gcc"), "gpp", []),
            (("--kind", "windows"), "msvc", ["win32"]),
            (("--layer", "gcc", "--layer", "windows"), "gpp", ["win32"]),
        )
        for arguments, toolchain, apis in cases:
            with self.subTest(arguments=arguments):
                legacy = self.generated(*arguments)
                canonical_arguments = ["--toolchain", toolchain] if toolchain else []
                for api in apis:
                    canonical_arguments.extend(["--api", api])
                self.assertEqual(self.generated(*canonical_arguments), legacy)

    def test_kind_and_layer_cannot_be_combined(self) -> None:
        result = subprocess.run([sys.executable, str(GENERATOR), "--kind", "gcc", "--layer", "windows", "--into", str(ROOT)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--kind and --layer cannot be combined", result.stderr)

    def test_legacy_and_explicit_selection_cannot_be_combined(self) -> None:
        result = subprocess.run([sys.executable, str(GENERATOR), "--kind", "windows", "--toolchain", "gpp", "--into", str(ROOT)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot be combined with --toolchain/--api", result.stderr)


if __name__ == "__main__":
    unittest.main()
