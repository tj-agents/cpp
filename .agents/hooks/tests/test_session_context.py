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
    def context(
        self,
        kind: str | None,
        platform: str,
        files: list[str],
        layers: list[str] | None = None,
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            if kind is not None or layers is not None:
                routes = root / ".agents" / "skill-routes.json"
                routes.parent.mkdir(parents=True)
                declaration = {"routes": []}
                if kind is not None:
                    declaration["kind"] = kind
                if layers is not None:
                    declaration["layers"] = layers
                routes.write_text(json.dumps(declaration), encoding="utf-8")
            with patch.object(session_context, "tracked_project", return_value=(root, files)):
                return session_context.context_for(root / "nested", platform)

    def test_gcc_route_wins_on_windows(self) -> None:
        context = self.context("gcc", "win32", ["app/src/main.cpp"])

        self.assertTrue(any("gcc:gcc-toolchain" in line for line in context))
        self.assertFalse(any("windows@cpp-agents" in line for line in context))

    def test_legacy_gpp_kind_maps_to_gcc(self) -> None:
        context = self.context("gpp", "win32", ["app/src/main.cpp"])

        self.assertTrue(any("gcc:gcc-toolchain" in line for line in context))

    def test_windows_route_wins_on_linux(self) -> None:
        context = self.context("windows", "linux", ["app/src/main.cpp"])

        self.assertTrue(any("windows:win32-style" in line for line in context))
        self.assertFalse(any("gcc@cpp-agents" in line for line in context))

    def test_generic_route_suppresses_host_layer(self) -> None:
        context = self.context("generic", "linux", ["app/src/main.cpp"])

        self.assertEqual(1, len(context))
        self.assertIn("base@cpp-agents", context[0])

    def test_legacy_portable_kind_maps_to_generic(self) -> None:
        context = self.context("portable", "linux", ["app/src/main.cpp"])

        self.assertEqual(1, len(context))

    def test_explicit_windows_and_gcc_layers_compose(self) -> None:
        context = self.context(
            None,
            "win32",
            ["app/src/main.cpp"],
            layers=["base", "windows", "gcc"],
        )

        self.assertEqual(3, len(context))
        self.assertTrue(any("base@cpp-agents" in line for line in context))
        self.assertTrue(any("windows@cpp-agents" in line for line in context))
        self.assertTrue(any("gcc@cpp-agents" in line for line in context))

    def test_versioned_compatibility_hook_emits_only_legacy_installed_namespaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed_hook = (
                root
                / "cache"
                / "cpp-agents"
                / "cpp-standards"
                / "0.3.0"
                / "hooks"
                / "session_context.py"
            )
            installed_hook.parent.mkdir(parents=True)
            shutil.copy2(
                ROOT / "plugins" / "cpp-standards" / "hooks" / "session_context.py",
                installed_hook,
            )
            installed_spec = importlib.util.spec_from_file_location(
                "installed_compatibility_session_context",
                installed_hook,
            )
            installed_module = importlib.util.module_from_spec(installed_spec)
            installed_spec.loader.exec_module(installed_module)
            routes = root / ".agents" / "skill-routes.json"
            routes.parent.mkdir(parents=True)
            routes.write_text(
                json.dumps({"layers": ["base", "windows", "gcc"], "routes": []}),
                encoding="utf-8",
            )
            with patch.object(
                installed_module,
                "tracked_project",
                return_value=(root, ["app/src/main.cpp"]),
            ):
                context = installed_module.context_for(root, "win32")

        combined = "\n".join(context)
        self.assertIn("cpp-standards:cpp-style", combined)
        self.assertIn("windows-standards:win32-style", combined)
        self.assertIn("gpp-standards:gpp-toolchain", combined)
        self.assertNotIn("base:", combined)
        self.assertNotIn("windows:win32-style", combined)
        self.assertNotIn("gcc:gcc-toolchain", combined)

    def test_windows_marker_is_read_from_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "app" / "src" / "main.cpp"
            source.parent.mkdir(parents=True)
            source.write_text("#include <windows.h>\n", encoding="utf-8")
            with patch.object(
                session_context,
                "tracked_project",
                return_value=(root, ["app/src/main.cpp"]),
            ):
                context = session_context.context_for(source.parent, "win32")

        self.assertTrue(any("windows:win32-style" in line for line in context))

    def test_windows_marker_after_two_hundred_sources_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = [f"src/{index:03}.cpp" for index in range(201)]
            for relative in files:
                source = root / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("int value;\n", encoding="utf-8")
            (root / files[200]).write_text("#include <windows.h>\n", encoding="utf-8")
            with patch.object(
                session_context,
                "tracked_project",
                return_value=(root, files),
            ):
                context = session_context.context_for(root, "linux")

        self.assertTrue(any("windows:win32-style" in line for line in context))
        self.assertFalse(any("gcc@cpp-agents" in line for line in context))

    def test_windows_detection_uses_git_grep_without_opening_sources(self) -> None:
        completed = session_context.subprocess.CompletedProcess([], 0)
        with patch.object(session_context.subprocess, "run", return_value=completed) as run:
            with patch.object(Path, "open", side_effect=AssertionError("source read")):
                detected = session_context.is_native_windows(
                    Path("repository"),
                    [f"src/{index:06}.cpp" for index in range(100000)],
                )

        self.assertTrue(detected)
        command = run.call_args.args[0]
        self.assertIn("grep", command)
        self.assertIn("--quiet", command)

    def test_non_cpp_repository_gets_no_context(self) -> None:
        self.assertEqual([], self.context(None, "linux", ["README.md"]))


if __name__ == "__main__":
    unittest.main()
