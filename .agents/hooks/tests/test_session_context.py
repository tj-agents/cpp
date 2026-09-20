import importlib.util
import json
import shutil
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
    def context(self, platform: str, files: list[str], profile: dict | None = None, kind: str | None = None) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            if profile is not None or kind is not None:
                routes = root / ".agents" / "skill-routes.json"
                routes.parent.mkdir(parents=True)
                declaration = {"routes": []}
                if profile is not None:
                    declaration["profile"] = profile
                if kind is not None:
                    declaration["kind"] = kind
                routes.write_text(json.dumps(declaration), encoding="utf-8")
            with patch.object(session_context, "tracked_project", return_value=(root, files)):
                return session_context.context_for(root / "nested", platform)

    def test_gpp_selection_does_not_follow_windows_host(self) -> None:
        context = self.context("win32", ["src/main.cpp"], {"toolchain": "gpp", "apis": []})
        combined = "\n".join(context)
        self.assertIn("gpp:gpp-toolchain", combined)
        self.assertNotIn("msvc:", combined)
        self.assertNotIn("win32:", combined)

    def test_msvc_alone_does_not_select_win32(self) -> None:
        context = self.context("win32", ["src/main.cpp"], {"toolchain": "msvc", "apis": []})
        combined = "\n".join(context)
        self.assertIn("msvc:msvc-toolchain", combined)
        self.assertNotIn("win32:win32-style", combined)

    def test_win32_does_not_require_a_toolchain(self) -> None:
        context = self.context("linux", ["src/main.cpp"], {"toolchain": None, "apis": ["win32"]})
        combined = "\n".join(context)
        self.assertIn("win32:win32-style", combined)
        self.assertNotIn("gpp:", combined)
        self.assertNotIn("msvc:", combined)

    def test_gpp_and_win32_compose(self) -> None:
        context = self.context("win32", ["src/main.cpp"], {"toolchain": "gpp", "apis": ["win32"]})
        combined = "\n".join(context)
        self.assertIn("cpp@cpp-agents", combined)
        self.assertIn("gpp:gpp-toolchain", combined)
        self.assertIn("win32:win32-style", combined)

    def test_host_os_never_selects_a_compiler(self) -> None:
        for platform in ("win32", "linux"):
            combined = "\n".join(self.context(platform, ["src/main.cpp"]))
            self.assertIn("cpp@cpp-agents", combined)
            self.assertNotIn("gpp:gpp-toolchain", combined)
            self.assertNotIn("msvc:msvc-toolchain", combined)

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
        self.assertNotIn("Apply win32@cpp-agents", combined)
        self.assertNotIn("msvc:msvc-toolchain", combined)

    def test_legacy_windows_kind_preserves_both_halves(self) -> None:
        combined = "\n".join(self.context("linux", ["src/main.cpp"], kind="windows"))
        self.assertIn("msvc:msvc-toolchain", combined)
        self.assertIn("win32:win32-style", combined)

    def test_compatibility_hook_uses_compatibility_namespaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed = root / "plugins/base/hooks/session_context.py"
            installed.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "plugins/base/hooks/session_context.py", installed)
            spec = importlib.util.spec_from_file_location("compat_hook", installed)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            routes = root / ".agents/skill-routes.json"
            routes.parent.mkdir(parents=True)
            routes.write_text(json.dumps({"profile": {"toolchain": "gpp", "apis": ["win32"]}}), encoding="utf-8")
            with patch.object(module, "tracked_project", return_value=(root, ["src/main.cpp"])):
                combined = "\n".join(module.context_for(root, "win32"))
        self.assertIn("base:cpp-style", combined)
        self.assertIn("gcc:gcc-toolchain", combined)
        self.assertIn("windows:win32-style", combined)
        self.assertNotIn("cpp:cpp-style", combined)

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
