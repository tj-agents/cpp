import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class HookContractTests(unittest.TestCase):
    def test_hook_manifests_register_the_current_host_payloads(self) -> None:
        for host in ("codex", "claude"):
            manifest = json.loads(
                (ROOT / f"plugins/cpp/.{host}-plugin/plugin.json").read_text()
            )
            self.assertEqual(f"./hooks/{host}.json", manifest["hooks"])
            payload = json.loads((ROOT / f"plugins/cpp/hooks/{host}.json").read_text())
            hook = payload["hooks"]["SessionStart"][0]["hooks"][0]
            self.assertIn("session_context.py", hook["command"])
            if host == "codex":
                self.assertIn("python -I -B -c", hook["commandWindows"])
                self.assertNotIn("$LASTEXITCODE", hook["commandWindows"])
                self.assertTrue(
                    (ROOT / "plugins/cpp/hooks/codex/snapshot.py").is_file()
                )

    def run_hook(self, host: str, tampered: bool) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="cpp native hook ") as temporary:
            directory = Path(temporary)
            package = directory / "installed plugins/cpp/local"
            shutil.copytree(ROOT / "plugins/cpp", package)
            repository = directory / "repository with spaces"
            repository.mkdir()
            (repository / "main.cpp").write_text("int main() {}\n")
            if tampered:
                with (package / "hooks/session_context.py").open("a") as stream:
                    stream.write("\nraise RuntimeError('tampered hook')\n")
            hook = json.loads((package / f"hooks/{host}.json").read_text())["hooks"][
                "SessionStart"
            ][0]["hooks"][0]
            environment = dict(
                os.environ,
                PLUGIN_ROOT=str(package),
                CLAUDE_PLUGIN_ROOT=str(package),
                PLUGIN_DATA=str(directory / "plugin data"),
                TJ_AGENTS_STARTUP_SNAPSHOT_DIRECTORY=str(directory / "snapshots"),
            )
            field = (
                "commandWindows" if host == "codex" and os.name == "nt" else "command"
            )
            command = (
                hook[field]
                .replace("${PLUGIN_ROOT}", str(package))
                .replace("${CLAUDE_PLUGIN_ROOT}", str(package))
            )
            shell = (
                f'cmd.exe /d /s /c "{command}"'
                if os.name == "nt"
                else ["sh", "-c", command]
            )
            return subprocess.run(
                shell,
                input=json.dumps({"cwd": str(repository)}),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=repository,
                env=environment,
                timeout=30,
            )

    def test_codex_command_executes_from_path_with_spaces(self) -> None:
        result = self.run_hook("codex", False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("This is a C++ repository", result.stdout)
        self.assertNotIn("cpp:knowledge", result.stdout)

    def test_codex_snapshot_rejects_modified_package_before_execution(self) -> None:
        result = self.run_hook("codex", True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("integrity", result.stderr.lower())
        self.assertNotIn("tampered hook", result.stderr)

    def test_claude_command_executes_from_path_with_spaces(self) -> None:
        result = self.run_hook("claude", False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("This is a C++ repository", result.stdout)

    def test_claude_command_preserves_failure(self) -> None:
        result = self.run_hook("claude", True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("tampered hook", result.stderr)
