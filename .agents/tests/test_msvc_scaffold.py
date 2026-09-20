import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins" / "msvc" / "resources" / "msvc" / "utility" / "scripts" / "New-MsvcProject.ps1"


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
            self.assertFalse((parent / "cpp23_app/.clang-format").exists())
            self.assertFalse((parent / "cpp23_app/.clang-tidy").exists())

            for project in (parent / "cpp20_app", parent / "cpp23_app"):
                json.loads((project / "CMakePresets.json").read_text(encoding="utf-8"))
                for script in (project / "scripts").glob("*.ps1"):
                    escaped = str(script).replace("'", "''")
                    parser = "$t=$null;$e=$null;[Management.Automation.Language.Parser]::ParseFile('" + escaped + "',[ref]$t,[ref]$e)|Out-Null;if($e.Count){exit 1}"
                    parsed = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", parser])
                    self.assertEqual(0, parsed.returncode, script)

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
