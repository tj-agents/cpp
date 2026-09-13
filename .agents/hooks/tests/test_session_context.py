import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


HOOK = Path(__file__).resolve().parents[1] / "session_context.py"
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

    def test_non_cpp_repository_gets_no_context(self) -> None:
        self.assertEqual([], self.context(None, "linux", ["README.md"]))


if __name__ == "__main__":
    unittest.main()
