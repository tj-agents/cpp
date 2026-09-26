import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("sync_generated", ROOT / ".agents/sync_generated.py")
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class HookContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output, cls.config = SYNC.build(ROOT)
        cls.packages = [
            *json.loads((ROOT / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))["publicPlugins"],
            *(name for name in cls.config["packages"] if name not in {"cpp", "gpp", "msvc", "win32"}),
        ]

    def validate(self, output: dict[str, bytes]) -> None:
        SYNC.validate_hook_outputs(output, self.config, self.packages)

    def test_hook_packages_register_host_specific_payloads(self) -> None:
        self.validate(self.output)
        for package in self.config["hook_packages"]:
            codex = json.loads(self.output[f"plugins/{package}/.codex-plugin/plugin.json"])
            claude = json.loads(self.output[f"plugins/{package}/.claude-plugin/plugin.json"])
            self.assertEqual("./hooks/codex.json", codex["hooks"])
            self.assertEqual("./hooks/claude.json", claude["hooks"])

    def test_shipped_hook_without_manifest_pointer_is_rejected(self) -> None:
        output = copy.deepcopy(self.output)
        path = "plugins/cpp/.codex-plugin/plugin.json"
        manifest = json.loads(output[path])
        manifest.pop("hooks")
        output[path] = json.dumps(manifest).encode()
        with self.assertRaisesRegex(ValueError, "hook pointer"):
            self.validate(output)

    def test_missing_hook_pointer_target_is_rejected(self) -> None:
        output = copy.deepcopy(self.output)
        del output["plugins/cpp/hooks/codex.json"]
        with self.assertRaisesRegex(ValueError, "shipped hooks disagree|target is missing"):
            self.validate(output)

    def test_missing_hook_script_target_is_rejected(self) -> None:
        output = copy.deepcopy(self.output)
        del output["plugins/cpp/hooks/session_context.py"]
        with self.assertRaisesRegex(ValueError, "script target is missing"):
            self.validate(output)

    def test_unknown_hook_type_is_rejected(self) -> None:
        output = copy.deepcopy(self.output)
        path = "plugins/cpp/hooks/codex.json"
        payload = json.loads(output[path])
        payload["hooks"]["SessionStart"][0]["hooks"][0]["type"] = "commnad"
        output[path] = json.dumps(payload).encode()
        with self.assertRaisesRegex(ValueError, "unsupported hook type"):
            self.validate(output)

    def test_codex_windows_python_root_resolution_is_enforced(self) -> None:
        output = copy.deepcopy(self.output)
        path = "plugins/cpp/hooks/codex.json"
        payload = json.loads(output[path])
        payload["hooks"]["SessionStart"][0]["hooks"][0]["commandWindows"] = (
            'python -B "${PLUGIN_ROOT}/hooks/session_context.py"; exit $LASTEXITCODE'
        )
        output[path] = json.dumps(payload).encode()
        with self.assertRaisesRegex(ValueError, "wrong plugin root"):
            self.validate(output)

    def test_codex_windows_exit_code_preservation_is_enforced(self) -> None:
        output = copy.deepcopy(self.output)
        path = "plugins/cpp/hooks/codex.json"
        payload = json.loads(output[path])
        command = payload["hooks"]["SessionStart"][0]["hooks"][0]["commandWindows"]
        payload["hooks"]["SessionStart"][0]["hooks"][0]["commandWindows"] = command.removesuffix(
            "; exit $LASTEXITCODE"
        )
        output[path] = json.dumps(payload).encode()
        with self.assertRaisesRegex(ValueError, "does not preserve the hook exit code"):
            self.validate(output)

    @unittest.skipUnless(os.name == "nt", "Windows command expansion requires cmd.exe")
    def test_every_codex_windows_hook_command_runs_from_a_path_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cpp hook contract ") as temporary:
            temporary = Path(temporary)
            repository = temporary / "repository"
            repository.mkdir()
            (repository / "main.cpp").write_text("int main() {}\n", encoding="utf-8")
            for package in self.config["hook_packages"]:
                package_root = temporary / "installed plugins" / package
                prefix = f"plugins/{package}/"
                for path, data in self.output.items():
                    if path.startswith(prefix):
                        destination = package_root / path.removeprefix(prefix)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(data)
                hooks = json.loads((package_root / "hooks/codex.json").read_text(encoding="utf-8"))["hooks"]
                environment = os.environ.copy()
                environment["PLUGIN_ROOT"] = str(package_root)
                for groups in hooks.values():
                    for group in groups:
                        for hook in group["hooks"]:
                            completed = subprocess.run(
                                ["pwsh", "-NoProfile", "-Command", hook["commandWindows"]],
                                input=json.dumps({"cwd": str(repository)}),
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="replace",
                                env=environment,
                                cwd=repository,
                            )
                            self.assertEqual(0, completed.returncode, completed.stderr)
                            self.assertTrue(completed.stdout.strip(), package)


if __name__ == "__main__":
    unittest.main()
