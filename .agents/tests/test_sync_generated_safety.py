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
            "scopes": [{"root": ".agents/base"}, {"root": ".agents/gpp"}, {"root": ".agents/msvc"}, {"root": ".agents/win32"}],
            "host_adapter_roots": {"agents": ".agents/skills", "codex": ".codex/skills", "claude": ".claude/skills"},
            "package_root": "plugins",
            "marketplace_outputs": {"codex": ".agents/plugins/marketplace.json", "claude": ".claude-plugin/marketplace.json"},
            "host_manifest_roots": {"codex": ".agents/plugins/manifests/codex", "claude": ".agents/plugins/manifests/claude"},
            "resources": [{"source": ".agents/msvc/utility/scripts"}],
            "generated_roots": [".agents/skills", ".codex/skills", ".claude/skills", "plugins", ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json", ".agents/base/INDEX.md", ".agents/gpp/INDEX.md", ".agents/msvc/INDEX.md", ".agents/win32/INDEX.md"],
        }

    def test_declared_adapter_and_exact_scope_index_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = sync_generated.validated_generated_roots(Path(temporary), self.config())
        self.assertEqual(10, len(paths))

    def test_repository_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = self.config()
            config["package_root"] = "."
            config["generated_roots"] = [value if value != "plugins" else "." for value in config["generated_roots"]]
            with self.assertRaisesRegex(ValueError, "Package root"):
                sync_generated.validated_generated_roots(Path(temporary), config)

    def test_arbitrary_tracked_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            for value in ("README.md", ".agents/tests", ".agents/sync_generated.py"):
                config = self.config()
                config["generated_roots"].append(value)
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, "disagree with the source map"):
                    sync_generated.validated_generated_roots(Path(temporary), config)

    def test_configured_output_paths_cannot_be_reassigned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            mutations = (
                ("package", "README.md", "Package root"),
                ("adapter", ".agents/tests", "Host adapter roots"),
                ("marketplace", ".agents/sync_generated.py", "Marketplace outputs"),
                ("scope", ".agents/other", "Scope roots"),
            )
            for kind, value, message in mutations:
                config = self.config()
                if kind == "package":
                    old = config["package_root"]
                    config["package_root"] = value
                elif kind == "adapter":
                    old = config["host_adapter_roots"]["agents"]
                    config["host_adapter_roots"]["agents"] = value
                elif kind == "marketplace":
                    old = config["marketplace_outputs"]["codex"]
                    config["marketplace_outputs"]["codex"] = value
                else:
                    old_root = config["scopes"][0]["root"]
                    config["scopes"][0]["root"] = value
                    old = f"{old_root}/INDEX.md"
                    value = f"{value}/INDEX.md"
                config["generated_roots"] = [value if item == old else item for item in config["generated_roots"]]
                with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, message):
                    sync_generated.validated_generated_roots(Path(temporary), config)

    def test_authored_scope_and_parent_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            for value in (".agents/base", ".agents"):
                config = self.config()
                config["package_root"] = value
                config["generated_roots"] = [value if item == "plugins" else item for item in config["generated_roots"]]
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Package root"):
                    sync_generated.validated_generated_roots(Path(temporary), config)

    def test_authored_resource_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = self.config()
            config["package_root"] = ".agents/msvc/utility/scripts"
            config["generated_roots"] = [config["package_root"] if item == "plugins" else item for item in config["generated_roots"]]
            with self.assertRaisesRegex(ValueError, "Package root"):
                sync_generated.validated_generated_roots(Path(temporary), config)

    def test_retired_reference_match_uses_exact_basename_boundaries(self) -> None:
        self.assertEqual(["STYLE.md", "WIN32.md"], sync_generated.retired_doc_references("See docs/STYLE.md and `WIN32.md`."))
        self.assertEqual([], sync_generated.retired_doc_references("See CODING_STYLE.md and PORTABLE_WIN32.md."))
        self.assertEqual([], sync_generated.retired_doc_references("Keep STYLE.md.bak, WIN32.md.old, and prefix.STYLE.md."))
        self.assertEqual(["STYLE.md", "WIN32.md"], sync_generated.retired_doc_references("See STYLE.md#rules and WIN32.md?plain=1."))


if __name__ == "__main__":
    unittest.main()
