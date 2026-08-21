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
    def context(self, kind: str | None, platform: str, files: list[str]) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            if kind is not None:
                routes = root / ".agents" / "skill-routes.json"
                routes.parent.mkdir(parents=True)
                routes.write_text(json.dumps({"kind": kind, "routes": []}), encoding="utf-8")
            with patch.object(session_context, "tracked_project", return_value=(root, files)):
                return session_context.context_for(root / "nested", platform)

    def test_gpp_route_wins_on_windows(self) -> None:
        context = self.context("gpp", "win32", ["app/src/main.cpp"])

        self.assertTrue(any("gpp-standards:gpp-toolchain" in line for line in context))
        self.assertFalse(any("windows-standards" in line for line in context))

    def test_windows_route_wins_on_linux(self) -> None:
        context = self.context("windows", "linux", ["app/src/main.cpp"])

        self.assertTrue(any("windows-standards" in line for line in context))
        self.assertFalse(any("gpp-standards" in line for line in context))

    def test_portable_route_suppresses_host_layer(self) -> None:
        context = self.context("portable", "linux", ["app/src/main.cpp"])

        self.assertEqual(1, len(context))

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

        self.assertTrue(any("windows-standards" in line for line in context))


if __name__ == "__main__":
    unittest.main()
