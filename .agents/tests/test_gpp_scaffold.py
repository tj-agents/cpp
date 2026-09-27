import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins" / "gpp" / "resources" / "gpp" / "utility" / "scripts" / "new-gpp-project.sh"
SHARED = ROOT / "plugins" / "gpp" / "resources" / "base" / "utility" / "scripts" / "templates"
# Resolve PATH explicitly: Windows CreateProcess otherwise checks system32 first.
BASH = shutil.which("bash") or "bash"


class GppScaffoldTests(unittest.TestCase):
    @staticmethod
    def bash_path(path: Path) -> str:
        resolved = path.resolve().as_posix()
        if os.name != "nt":
            return resolved
        if len(resolved) < 3 or resolved[1:3] != ":/":
            raise RuntimeError(f"Unsupported Windows path for Bash: {resolved}")
        if subprocess.run([BASH, "-lc", "test -d /mnt/c"], check=False).returncode == 0:
            prefix = "/mnt/"
        elif subprocess.run([BASH, "-lc", "test -d /c"], check=False).returncode == 0:
            prefix = "/"
        else:
            raise RuntimeError("Bash exposes neither WSL nor Git Bash drive mounts")
        return f"{prefix}{resolved[0].lower()}{resolved[2:]}"

    def run_scaffold(self, *arguments: str, script: Path = SCRIPT) -> subprocess.CompletedProcess[str]:
        converted = list(arguments)
        if "--destination" in converted:
            index = converted.index("--destination") + 1
            converted[index] = self.bash_path(Path(converted[index]))
        return subprocess.run(
            [BASH, self.bash_path(script), *converted],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_cpp20_cpp23_and_bash_parse(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cpp agents scaffold ") as temporary:
            parent = Path(temporary) / "parent with spaces"
            parent.mkdir()

            cpp20 = self.run_scaffold("--name", "cpp20_app", "--destination", str(parent), "--cpp-standard", "20")
            self.assertEqual(0, cpp20.returncode, cpp20.stdout + cpp20.stderr)
            cpp23 = self.run_scaffold("--name", "cpp23_app", "--destination", str(parent), "--cpp-standard", "23")
            self.assertEqual(0, cpp23.returncode, cpp23.stdout + cpp23.stderr)

            self.assertIn("CMAKE_CXX_STANDARD 20", (parent / "cpp20_app/CMakeLists.txt").read_text(encoding="utf-8"))
            self.assertIn("CMAKE_CXX_STANDARD 23", (parent / "cpp23_app/CMakeLists.txt").read_text(encoding="utf-8"))

            for project in (parent / "cpp20_app", parent / "cpp23_app"):
                json.loads((project / "CMakePresets.json").read_text(encoding="utf-8"))
                parsed = subprocess.run([BASH, "-n", self.bash_path(SCRIPT)])
                self.assertEqual(0, parsed.returncode, "new-gpp-project.sh")

    def test_generated_sources_actually_compile_under_each_standard(self) -> None:
        gxx = shutil.which("g++")
        if not gxx:
            self.skipTest("g++ not available")
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            for standard in ("20", "23"):
                name = f"compile_check_{standard}"
                created = self.run_scaffold("--name", name, "--destination", str(parent), "--cpp-standard", standard)
                self.assertEqual(0, created.returncode, created.stdout + created.stderr)
                project = parent / name
                binary = parent / f"{name}.bin"
                compiled = subprocess.run(
                    [
                        gxx, f"-std=c++{standard}",
                        "-I", str(project / "libs/core/include"),
                        str(project / "app/src/main.cpp"),
                        str(project / "libs/core/src/core.cpp"),
                        "-o", str(binary),
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, compiled.returncode, compiled.stdout + compiled.stderr)
                run = subprocess.run([str(binary)], capture_output=True, text=True)
                self.assertEqual(0, run.returncode)
                self.assertIn(name, run.stdout)

                simple_name = f"{name}_simple"
                simple = self.run_scaffold("--name", simple_name, "--destination", str(parent), "--cpp-standard", standard, "--simple")
                self.assertEqual(0, simple.returncode, simple.stdout + simple.stderr)
                simple_binary = parent / f"{simple_name}.bin"
                simple_compiled = subprocess.run(
                    [gxx, f"-std=c++{standard}", str(parent / simple_name / "main.cpp"), "-o", str(simple_binary)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, simple_compiled.returncode, simple_compiled.stdout + simple_compiled.stderr)

    def test_project_layout_configuration_and_route_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            created = self.run_scaffold("--name", "my-tool", "--destination", str(parent))
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            project = parent / "my-tool"
            expected = {
                ".agents/skill-routes.json",
                ".clang-format",
                ".clang-tidy",
                ".clangd",
                ".editorconfig",
                ".gitignore",
                ".vscode/extensions.json",
                ".vscode/launch.json",
                ".vscode/settings.json",
                "AGENTS.md",
                "CLAUDE.md",
                "CMakeLists.txt",
                "CMakePresets.json",
                "README.md",
                "app/CMakeLists.txt",
                "app/src/main.cpp",
                "libs/core/CMakeLists.txt",
                "libs/core/include/core/core.hpp",
                "libs/core/src/core.cpp",
                "tests/CMakeLists.txt",
                "tests/core/core_test.cpp",
            }
            actual = {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file()}
            self.assertEqual(expected, actual)
            for name in (".clang-format", ".clang-tidy", ".editorconfig"):
                self.assertEqual((SHARED / f"{name}.in").read_bytes(), (project / name).read_bytes())
            routes = json.loads((project / ".agents/skill-routes.json").read_text(encoding="utf-8"))
            self.assertEqual({"toolchain": "gpp", "apis": []}, routes["profile"])
            self.assertEqual(["cpp", "gpp"], routes["layers"])
            presets = json.loads((project / "CMakePresets.json").read_text(encoding="utf-8"))
            configure = {preset["name"]: preset for preset in presets["configurePresets"]}
            self.assertEqual({"dev", "release", "gdb"}, set(configure))
            self.assertEqual("ON", configure["dev"]["cacheVariables"]["MY_TOOL_SANITIZE"])
            self.assertNotIn("CMAKE_CXX_FLAGS", configure["dev"]["cacheVariables"])
            self.assertNotIn("MY_TOOL_SANITIZE", configure["gdb"]["cacheVariables"])
            self.assertIn("set(CMAKE_CXX_SCAN_FOR_MODULES OFF)", (project / "CMakeLists.txt").read_text(encoding="utf-8"))
            launch = json.loads((project / ".vscode/launch.json").read_text(encoding="utf-8"))
            self.assertEqual("gdb", launch["configurations"][0]["MIMode"])

    def test_project_builds_and_runs_with_cmake_presets(self) -> None:
        gxx = shutil.which("g++")
        if not gxx or not shutil.which("cmake") or not shutil.which("ninja"):
            self.skipTest("g++, CMake or Ninja not available")
        # MinGW ships no sanitizer runtimes, so only the gdb preset is portable there.
        presets = ["gdb"] if os.name == "nt" else ["gdb", "dev"]
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            created = self.run_scaffold("--name", "built", "--destination", str(parent))
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            project = parent / "built"
            for preset in presets:
                # Tests are not built: Catch2 would be downloaded. Every owned target is.
                configured = subprocess.run(
                    ["cmake", "--preset", preset, f"-DCMAKE_CXX_COMPILER={gxx}", "-DBUILD_TESTING=OFF", "-DBUILT_WARNINGS_AS_ERRORS=ON"],
                    cwd=project, capture_output=True, text=True,
                )
                self.assertEqual(0, configured.returncode, configured.stdout + configured.stderr)
                built = subprocess.run(["cmake", "--build", "--preset", preset], cwd=project, capture_output=True, text=True)
                self.assertEqual(0, built.returncode, built.stdout + built.stderr)
                binary = project / "build" / preset / "bin" / ("built.exe" if os.name == "nt" else "built")
                run = subprocess.run([str(binary)], capture_output=True, text=True)
                self.assertEqual(0, run.returncode, run.stderr)
                self.assertIn("hello from built", run.stdout)

    def test_simple_variant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary) / "destination"
            parent.mkdir()
            simple = self.run_scaffold("--name", "leetcode_thing", "--destination", str(parent), "--simple")
            self.assertEqual(0, simple.returncode, simple.stdout + simple.stderr)
            created = {p.name for p in (parent / "leetcode_thing").iterdir()}
            self.assertEqual({"CMakeLists.txt", "main.cpp"}, created)

    def test_dry_run_existing_destination_and_missing_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary) / "destination"
            parent.mkdir()
            preview = self.run_scaffold("--name", "preview", "--destination", str(parent), "--dry-run")
            self.assertEqual(0, preview.returncode, preview.stdout + preview.stderr)
            self.assertFalse((parent / "preview").exists())

            existing = parent / "existing"
            existing.mkdir()
            refused = self.run_scaffold("--name", "existing", "--destination", str(parent))
            self.assertNotEqual(0, refused.returncode)
            self.assertIn("Destination already exists", refused.stdout + refused.stderr)

            isolated = Path(temporary) / "isolated" / "new-gpp-project.sh"
            isolated.parent.mkdir()
            shutil.copy2(SCRIPT, isolated)
            missing = self.run_scaffold("--name", "missing", "--destination", str(parent), script=isolated)
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("templates are missing", missing.stdout + missing.stderr)

    def test_invalid_name_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            invalid = self.run_scaffold("--name", "../escape", "--destination", str(parent))
            self.assertNotEqual(0, invalid.returncode)
            self.assertFalse((parent.parent / "escape").exists())


if __name__ == "__main__":
    unittest.main()
