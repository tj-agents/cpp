from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / ".agents/sync_generated.py"
SPEC = importlib.util.spec_from_file_location("sync_generated", MODULE_PATH)
sync_generated = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_generated)


class GeneratedRootSafetyTests(unittest.TestCase):
    def config(self) -> dict:
        return {
            "scopes": [{"root": ".agents/base"}, {"root": ".agents/gpp"}, {"root": ".agents/msvc"}, {"root": ".agents/win32"}],
            "host_adapter_roots": {"codex": ".codex/skills", "claude": ".claude/skills"},
            "package_root": "plugins",
            "marketplace_outputs": {"codex": ".agents/plugins/marketplace.json", "claude": ".claude-plugin/marketplace.json"},
            "host_manifest_roots": {"codex": ".agents/plugins/manifests/codex", "claude": ".agents/plugins/manifests/claude"},
            "resources": [{"source": ".agents/msvc/utility/scripts"}],
            "generated_roots": [".codex/skills", ".claude/skills", "plugins", ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json", ".agents/base/INDEX.md", ".agents/gpp/INDEX.md", ".agents/msvc/INDEX.md", ".agents/win32/INDEX.md"],
        }

    def test_declared_adapter_and_exact_scope_index_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = sync_generated.validated_generated_roots(Path(temporary), self.config())
        self.assertEqual(9, len(paths))

    def test_source_map_has_only_host_specific_adapter_roots(self) -> None:
        config = json.loads((ROOT / ".agents/plugins/sources.json").read_text(encoding="utf-8"))
        self.assertEqual({"codex": ".codex/skills", "claude": ".claude/skills"}, config["host_adapter_roots"])
        self.assertNotIn(".agents/skills", config["generated_roots"])
        self.assertFalse((ROOT / ".agents/skills").exists())

    def test_generated_root_link_ancestor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".codex").mkdir()
            original = Path.is_symlink
            with mock.patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path.name == ".codex" or original(path)):
                with self.assertRaisesRegex(ValueError, "ancestor"):
                    sync_generated.validated_generated_roots(root, self.config())

    def test_retired_generated_root_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = Path.is_symlink
            with mock.patch.object(
                Path,
                "is_symlink",
                autospec=True,
                side_effect=lambda path: path.as_posix().endswith("/.agents/skills") or original(path),
            ):
                with self.assertRaisesRegex(ValueError, "Retired generated root ancestor"):
                    sync_generated.validated_retired_generated_roots(root)

    def test_text_resources_are_normalized_to_lf(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            resource = Path(temporary) / "script.sh"
            resource.write_bytes(b"#!/usr/bin/env bash\r\nset -euo pipefail\r\n")
            self.assertEqual(
                b"#!/usr/bin/env bash\nset -euo pipefail\n",
                sync_generated.resource_bytes(resource, text=True),
            )

    def test_retired_generated_root_is_reported_and_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            retired_file = root / ".agents/skills/example/SKILL.md"
            retired_file.parent.mkdir(parents=True)
            retired_file.write_text("stale", encoding="utf-8")
            config = self.config()
            with mock.patch.object(sync_generated, "build", return_value=({}, config)), mock.patch.object(
                sync_generated, "discover", return_value={}
            ):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(1, sync_generated.synchronize(root, check=True))
                self.assertIn("RETIRED: .agents/skills", output.getvalue())
                self.assertTrue(retired_file.exists())
                self.assertEqual(0, sync_generated.synchronize(root, check=False))
            self.assertFalse((root / ".agents/skills").exists())

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
                    old = config["host_adapter_roots"]["codex"]
                    config["host_adapter_roots"]["codex"] = value
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
        self.assertEqual([], sync_generated.retired_doc_references("Keep STYLE.md.bak, WIN32.md.old, prefix.STYLE.md, and STYLE.md/path."))
        self.assertEqual(["STYLE.md", "WIN32.md"], sync_generated.retired_doc_references("See STYLE.md#rules and WIN32.md?plain=1."))
        self.assertEqual(["STYLE.md"], sync_generated.retired_doc_references("Use 'STYLE.md', **STYLE.md**, or STYLE.md!"))
        self.assertEqual(["STYLE.md"], sync_generated.retired_doc_references("A sentence names STYLE.md. Then it ends with STYLE.md."))


if __name__ == "__main__":
    unittest.main()
