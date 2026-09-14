import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATTESTER = ROOT / ".agents" / "attest-external-contract.ps1"


class AttesterSafetyTests(unittest.TestCase):
    def test_attester_parses_as_powershell(self) -> None:
        attester_path = str(ATTESTER).replace("'", "''")
        parser = (
            "$tokens = $null; $errors = $null; "
            f"[Management.Automation.Language.Parser]::ParseFile('{attester_path}', "
            "[ref]$tokens, [ref]$errors) | Out-Null; "
            "if ($errors.Count) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }"
        )
        subprocess.run(
            ["pwsh", "-NoProfile", "-NonInteractive", "-Command", parser],
            check=True,
        )

    def test_all_git_and_gh_launches_use_captured_absolute_paths(self) -> None:
        source = ATTESTER.read_text(encoding="utf-8")
        set_location = source.index("Set-Location -LiteralPath $trustedRoot")
        resolve_git = source.index("$gitExecutable = (Get-Command git -CommandType Application")
        resolve_gh = source.index("$ghExecutable = (Get-Command gh -CommandType Application")
        self.assertLess(set_location, resolve_git)
        self.assertLess(set_location, resolve_gh)
        self.assertIn("$start.FileName = $gitExecutable", source)
        self.assertIn("foreach ($executable in @($gitExecutable, $ghExecutable))", source)
        self.assertIn("Test-PathWithin -Path $executable -Root $consumerRoot", source)

        resolution_prefix = source[:resolve_git]
        execution_body = source[source.index("if ($CandidateSha -notmatch"):]
        self.assertNotRegex(resolution_prefix, r"(?m)^\s*&\s+(?:git|gh)(?:\.exe)?\b")
        self.assertNotRegex(execution_body, r"(?m)^\s*&\s+(?:git|gh)(?:\.exe)?\b")
        self.assertNotRegex(execution_body, r"(?m)\|\s*(?:git|gh)(?:\.exe)?\s")
        self.assertNotIn('$start.FileName = "git"', execution_body)
        self.assertNotIn('$start.FileName = "gh"', execution_body)

    @unittest.skipUnless(os.name == "nt", "Windows command resolution regression")
    def test_candidate_path_executables_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            candidate = temporary / "candidate"
            producer = temporary / "producer"
            candidate.mkdir()
            producer.mkdir()
            system_executable = Path(os.environ["SystemRoot"]) / "System32" / "where.exe"
            shutil.copy2(system_executable, candidate / "git.exe")
            shutil.copy2(system_executable, candidate / "gh.exe")

            result = self.run_attester(candidate, producer, f"{candidate}{os.pathsep}{os.environ['PATH']}")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("Refusing candidate-owned executable", result.stdout + result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows command resolution regression")
    def test_candidate_current_directory_is_not_used_for_tool_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            candidate = temporary / "candidate"
            producer = temporary / "producer"
            candidate.mkdir()
            producer.mkdir()
            system_executable = Path(os.environ["SystemRoot"]) / "System32" / "where.exe"
            shutil.copy2(system_executable, candidate / "git.exe")
            shutil.copy2(system_executable, candidate / "gh.exe")

            result = self.run_attester(candidate, producer, os.environ["PATH"])

            self.assertNotEqual(0, result.returncode)
            output = result.stdout + result.stderr
            self.assertIn("CandidateSha must be a full lowercase Git commit SHA", output)
            self.assertNotIn("Refusing candidate-owned executable", output)

    @staticmethod
    def run_attester(candidate: Path, producer: Path, path_value: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PATH"] = path_value
        return subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(ATTESTER),
                "-ConsumerSource",
                str(candidate),
                "-CandidateSha",
                "invalid",
                "-AgentStandardsSource",
                str(producer),
            ],
            cwd=candidate,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )


if __name__ == "__main__":
    unittest.main()
