import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins" / "gpp" / "resources" / "gpp" / "utility" / "scripts" / "new-gpp-project.sh"


class GppScaffoldTests(unittest.TestCase):
    def run_scaffold(self, *arguments: str, script: Path = SCRIPT) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(script), *arguments],
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
                parsed = subprocess.run(["bash", "-n", str(SCRIPT)])
                self.assertEqual(0, parsed.returncode, "new-gpp-project.sh")

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
