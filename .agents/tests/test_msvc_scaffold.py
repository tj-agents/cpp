import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins" / "msvc" / "resources" / "msvc" / "utility" / "scripts" / "New-MsvcProject.ps1"
SHARED = ROOT / "plugins" / "msvc" / "resources" / "base" / "utility" / "scripts" / "templates"
VSWHERE = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Microsoft Visual Studio/Installer/vswhere.exe"


def build_with_msvc(project: Path) -> subprocess.CompletedProcess[str]:
    # Tests are not built: Catch2 would be downloaded. Compile and link every owned target.
    escaped = str(project).replace("'", "''")
    command = (
        f"$ErrorActionPreference='Stop'; Set-Location -LiteralPath '{escaped}'; "
        "& ./scripts/Enter-DevShell.ps1 *> $null; "
        "cmake --preset dev -DBUILD_TESTING=OFF; if ($LASTEXITCODE) { exit $LASTEXITCODE }; "
        "cmake --build --preset dev; exit $LASTEXITCODE"
    )
    # An MSYS2/MinGW CMake ahead on PATH must not be used for MSVC resource compilation.
    environment = dict(os.environ)
    msys = Path("C:/msys64/mingw64/bin")
    if (msys / "cmake.exe").is_file():
        environment["PATH"] = f"{msys}{os.pathsep}{environment['PATH']}"
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )


class MsvcScaffoldTests(unittest.TestCase):
    def run_scaffold(self, *arguments: str, script: Path = SCRIPT) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(script), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_cpp20_cpp23_spaces_config_copy_and_powershell_parse(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cpp agents scaffold ") as temporary:
            parent = Path(temporary) / "parent with spaces"
            parent.mkdir()
            format_config = Path(temporary) / "source format"
            tidy_config = Path(temporary) / "source tidy"
            format_bytes = b"BasedOnStyle: LLVM\r\n"
            tidy_bytes = b"Checks: '-*,modernize-*'\n"
            format_config.write_bytes(format_bytes)
            tidy_config.write_bytes(tidy_bytes)

            cpp20 = self.run_scaffold("-Name", "cpp20_app", "-Destination", str(parent), "-CppStandard", "20", "-FormatConfig", str(format_config), "-TidyConfig", str(tidy_config))
            self.assertEqual(0, cpp20.returncode, cpp20.stdout + cpp20.stderr)
            cpp23 = self.run_scaffold("-Name", "cpp23_app", "-Destination", str(parent), "-CppStandard", "23")
            self.assertEqual(0, cpp23.returncode, cpp23.stdout + cpp23.stderr)

            self.assertIn("cxx_std_20", (parent / "cpp20_app/CMakeLists.txt").read_text(encoding="utf-8"))
            self.assertIn("cxx_std_23", (parent / "cpp23_app/CMakeLists.txt").read_text(encoding="utf-8"))
            self.assertEqual(format_bytes, (parent / "cpp20_app/.clang-format").read_bytes())
            self.assertEqual(tidy_bytes, (parent / "cpp20_app/.clang-tidy").read_bytes())
            for name in (".clang-format", ".clang-tidy"):
                self.assertEqual((SHARED / f"{name}.in").read_bytes(), (parent / "cpp23_app" / name).read_bytes())

            for project in (parent / "cpp20_app", parent / "cpp23_app"):
                json.loads((project / "CMakePresets.json").read_text(encoding="utf-8"))
                for script in (project / "scripts").glob("*.ps1"):
                    escaped = str(script).replace("'", "''")
                    parser = "$t=$null;$e=$null;[Management.Automation.Language.Parser]::ParseFile('" + escaped + "',[ref]$t,[ref]$e)|Out-Null;if($e.Count){exit 1}"
                    parsed = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", parser])
                    self.assertEqual(0, parsed.returncode, script)

    def test_project_layout_matches_gpp_scaffold_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            created = self.run_scaffold("-Name", "my-tool", "-Destination", str(parent))
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            project = parent / "my-tool"

            expected = {
                "CMakeLists.txt",
                "CMakePresets.json",
                ".gitignore",
                "README.md",
                "libs/core/CMakeLists.txt",
                "libs/core/include/core/core.hpp",
                "libs/core/src/core.cpp",
                "app/CMakeLists.txt",
                "app/src/main.cpp",
                "tests/CMakeLists.txt",
                "tests/core/core_test.cpp",
                "scripts/Build.ps1",
                "scripts/Enter-DevShell.ps1",
                ".clang-format",
                ".clang-tidy",
                ".clangd",
                ".editorconfig",
                ".vscode/settings.json",
                ".vscode/launch.json",
                "AGENTS.md",
                "CLAUDE.md",
                ".agents/skill-routes.json",
            }
            actual = {str(p.relative_to(project)).replace("\\", "/") for p in project.rglob("*") if p.is_file()}
            self.assertEqual(expected, actual)

            # A dashed name is not a valid C++ identifier, so it must be sanitized
            # for the namespace/target tokens the same way new-gpp-project.sh does.
            header = (project / "libs/core/include/core/core.hpp").read_text(encoding="utf-8")
            self.assertIn("namespace my_tool {", header)
            core_source = (project / "libs/core/src/core.cpp").read_text(encoding="utf-8")
            self.assertIn('"hello from my-tool"', core_source)
            main_source = (project / "app/src/main.cpp").read_text(encoding="utf-8")
            self.assertIn("my_tool::greeting()", main_source)
            test_source = (project / "tests/core/core_test.cpp").read_text(encoding="utf-8")
            self.assertIn('my_tool::greeting() == "hello from my-tool"', test_source)

            routes = json.loads((project / ".agents/skill-routes.json").read_text(encoding="utf-8"))
            self.assertEqual({"toolchain": "msvc", "apis": []}, routes["profile"])
            self.assertEqual(["cpp", "msvc"], routes["layers"])
            cmake = (project / "CMakeLists.txt").read_text(encoding="utf-8")
            self.assertIn("add_library(my_tool_sanitize INTERFACE)", cmake)
            self.assertIn("/fsanitize=address", cmake)
            presets = json.loads((project / "CMakePresets.json").read_text(encoding="utf-8"))
            self.assertEqual({"dev", "release", "asan"}, {preset["name"] for preset in presets["configurePresets"]})
            launch = json.loads((project / ".vscode/launch.json").read_text(encoding="utf-8"))
            self.assertEqual("cppvsdbg", launch["configurations"][0]["type"])

    def test_console_project_builds_and_runs_with_real_msvc(self) -> None:
        if not VSWHERE.is_file() or not shutil.which("cmake") or not shutil.which("ninja"):
            self.skipTest("MSVC, CMake or Ninja not available")
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            created = self.run_scaffold("-Name", "console", "-Destination", str(parent))
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            built = build_with_msvc(parent / "console")
            self.assertEqual(0, built.returncode, built.stdout + built.stderr)
            run = subprocess.run([str(parent / "console/build/dev/bin/console.exe")], capture_output=True, text=True)
            self.assertEqual(0, run.returncode)
            self.assertIn("hello from console", run.stdout)

    def test_whatif_existing_destination_and_missing_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary) / "destination"
            parent.mkdir()
            preview = self.run_scaffold("-Name", "preview", "-Destination", str(parent), "-WhatIf")
            self.assertEqual(0, preview.returncode, preview.stdout + preview.stderr)
            self.assertFalse((parent / "preview").exists())

            existing = parent / "existing"
            existing.mkdir()
            refused = self.run_scaffold("-Name", "existing", "-Destination", str(parent))
            self.assertNotEqual(0, refused.returncode)
            self.assertIn("Destination already exists", refused.stdout + refused.stderr)

            isolated = Path(temporary) / "isolated" / "New-MsvcProject.ps1"
            isolated.parent.mkdir()
            shutil.copy2(SCRIPT, isolated)
            missing = self.run_scaffold("-Name", "missing", "-Destination", str(parent), script=isolated)
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("templates are missing", missing.stdout + missing.stderr)


if __name__ == "__main__":
    unittest.main()
