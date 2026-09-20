import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / ".agents/sync_generated.py"
SPEC = importlib.util.spec_from_file_location("sync_generated", MODULE_PATH)
sync_generated = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_generated)


class GeneratedRootSafetyTests(unittest.TestCase):
    def config(self) -> dict:
        return {
            "scopes": [{"root": ".agents/base"}],
            "host_manifest_roots": {"codex": ".agents/plugins/manifests/codex", "claude": ".agents/plugins/manifests/claude"},
            "resources": [{"source": ".agents/msvc/utility/scripts"}],
            "generated_roots": [".agents/skills", ".agents/base/INDEX.md"],
        }

    def test_declared_adapter_and_exact_scope_index_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = sync_generated.validated_generated_roots(Path(temporary), self.config())
        self.assertEqual(2, len(paths))

    def test_repository_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = self.config()
            config["generated_roots"] = ["."]
            with self.assertRaisesRegex(ValueError, "equals repository root"):
                sync_generated.validated_generated_roots(Path(temporary), config)

    def test_authored_scope_and_parent_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            for value in (".agents/base", ".agents"):
                config = self.config()
                config["generated_roots"] = [value]
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, "overlaps authored source"):
                    sync_generated.validated_generated_roots(Path(temporary), config)

    def test_authored_resource_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = self.config()
            config["generated_roots"] = [".agents/msvc/utility/scripts"]
            with self.assertRaisesRegex(ValueError, "overlaps authored source"):
                sync_generated.validated_generated_roots(Path(temporary), config)


if __name__ == "__main__":
    unittest.main()
