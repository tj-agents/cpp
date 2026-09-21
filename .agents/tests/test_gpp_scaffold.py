import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins" / "gpp" / "resources" / "gpp" / "utility" / "scripts" / "new-gpp-project.sh"


class GppScaffoldTests(unittest.TestCase):
    @staticmethod
    def bash_path(path: Path) -> str:
        resolved = path.resolve().as_posix()
        if os.name != "nt":
            return resolved
        if len(resolved) < 3 or resolved[1:3] != ":/":
            raise RuntimeError(f"Unsupported Windows path for Bash: {resolved}")
        if subprocess.run(["bash", "-lc", "test -d /mnt/c"], check=False).returncode == 0:
            prefix = "/mnt/"
        elif subprocess.run(["bash", "-lc", "test -d /c"], check=False).returncode == 0:
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
            ["bash", self.bash_path(script), *converted],
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
                parsed = subprocess.run(["bash", "-n", self.bash_path(SCRIPT)])
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
