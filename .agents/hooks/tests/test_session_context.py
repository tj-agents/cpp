import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HOOK = Path(__file__).resolve().parents[1] / "session_context.py"
ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("session_context", HOOK)
session_context = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(session_context)


class SessionContextTests(unittest.TestCase):
    def context(self, platform: str, files: list[str]) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(session_context, "tracked_project", return_value=(root, files)):
                return session_context.context_for(root / "nested", platform)

    def test_host_os_never_selects_a_compiler(self) -> None:
        for platform in ("win32", "linux"):
            combined = "\n".join(self.context(platform, ["src/main.cpp"]))
            self.assertIn("cpp@tj-agents", combined)
            self.assertNotIn("gpp:toolchain", combined)
            self.assertNotIn("msvc:toolchain", combined)

    def test_detected_win32_is_only_a_suggestion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "src/main.cpp"
            source.parent.mkdir()
            source.write_text("#include <windows.h>\n", encoding="utf-8")
            with patch.object(session_context, "tracked_project", return_value=(root, ["src/main.cpp"])):
                context = session_context.context_for(root, "win32")
        combined = "\n".join(context)
        self.assertIn("Consider selecting win32 explicitly", combined)
        self.assertNotIn("Apply win32@tj-agents", combined)
        self.assertNotIn("msvc:toolchain", combined)

    def test_windows_detection_uses_git_grep_without_opening_sources(self) -> None:
        completed = session_context.subprocess.CompletedProcess([], 0)
        with patch.object(session_context.subprocess, "run", return_value=completed) as run:
            with patch.object(Path, "open", side_effect=AssertionError("source read")):
                detected = session_context.is_native_windows(Path("repository"), [f"src/{index:06}.cpp" for index in range(100000)])
        self.assertTrue(detected)
        self.assertIn("grep", run.call_args.args[0])

    def test_non_cpp_repository_gets_no_context(self) -> None:
        self.assertEqual([], self.context("linux", ["README.md"]))


if __name__ == "__main__":
    unittest.main()
