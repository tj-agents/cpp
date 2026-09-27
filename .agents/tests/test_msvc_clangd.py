import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "plugins" / "msvc" / "resources" / "msvc" / "utility" / "scripts"
INSTALLER = SCRIPTS / "Install-ClangdMsvc.ps1"


class ClangdMsvcInstallerTests(unittest.TestCase):
    def install(self, install_directory: Path, settings: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(INSTALLER),
             "-InstallDirectory", str(install_directory), "-SettingsPath", str(settings)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_installs_crlf_launcher_and_preserves_existing_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            install_directory = Path(temporary) / "install dir"
            settings = Path(temporary) / "User" / "settings.json"
            settings.parent.mkdir()
            settings.write_text('{"files.autoSave": "afterDelay", "clangd.path": "old"}', encoding="utf-8")

            installed = self.install(install_directory, settings)
            self.assertEqual(0, installed.returncode, installed.stdout + installed.stderr)

            launcher = install_directory / "clangd-msvc.cmd"
            lines = (SCRIPTS / "clangd-msvc.cmd").read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(lines.replace(b"\n", b"\r\n"), launcher.read_bytes())
            written = json.loads(settings.read_text(encoding="utf-8"))
            self.assertEqual("afterDelay", written["files.autoSave"])
            self.assertEqual(str(launcher), written["clangd.path"])
            self.assertIs(True, written["clangd.useScriptAsExecutable"])

    def test_commented_settings_are_left_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            settings = Path(temporary) / "settings.json"
            original = '{\n  // keep me\n  "files.autoSave": "off"\n}\n'
            settings.write_text(original, encoding="utf-8")

            installed = self.install(Path(temporary) / "install", settings)
            self.assertEqual(0, installed.returncode, installed.stdout + installed.stderr)
            self.assertEqual(original, settings.read_text(encoding="utf-8"))
            self.assertIn("clangd.useScriptAsExecutable", installed.stdout)

    def test_launcher_writes_nothing_but_clangd_to_stdout(self) -> None:
        # stdout carries the language-server protocol, so developer-environment banners
        # printed before clangd starts would corrupt the session.
        text = (SCRIPTS / "clangd-msvc.cmd").read_text(encoding="utf-8")
        self.assertIn('vcvars64.bat" >nul 2>&1', text)
        self.assertIn("-requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64", text)


if __name__ == "__main__":
    unittest.main()
