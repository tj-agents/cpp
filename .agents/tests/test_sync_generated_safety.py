from contextlib import redirect_stdout
import copy
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


class SkillMappingTests(unittest.TestCase):
    def test_discovery_namespaces_repeated_short_names_by_plugin(self) -> None:
        config = {"scopes": [
            {"name": scope, "root": f".agents/{scope}", "layout": "kind", "plugin": plugin, "domain": "cpp"}
            for scope, plugin in (("base", "cpp"), ("gpp", "gpp"), ("msvc", "msvc"), ("win32", "win32"))
        ]}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for scope in config["scopes"]:
                path = root / scope["root"] / "contract" / "style" / "SKILL.md"
                path.parent.mkdir(parents=True)
                path.write_text("---\nname: style\ndescription: Example.\nkind: contract\ndomain: cpp\n---\n\n# Style\n", encoding="utf-8")
            skills = sync_generated.discover(root, config)
            self.assertEqual({"cpp:style", "gpp:style", "msvc:style", "win32:style"}, set(skills))
            duplicate = root / ".agents/base/knowledge/style/SKILL.md"
            duplicate.parent.mkdir(parents=True)
            duplicate.write_text("---\nname: style\ndescription: Example.\nkind: knowledge\ndomain: cpp\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate public skill identifier: cpp:style"):
                sync_generated.discover(root, config)

    def test_identifier_rewrites_are_exact_and_do_not_cascade(self) -> None:
        body = "cpp:style cpp:style-guide cpp:style_extra prefix-cpp:style docs/cpp:style cpp:build std::string"
        rewrites = {"cpp:style": "cpp:build", "cpp:build": "base:cpp-build"}
        self.assertEqual(
            "cpp:build cpp:style-guide cpp:style_extra prefix-cpp:style docs/cpp:style base:cpp-build std::string",
            sync_generated.rewrite_identifiers(body, rewrites),
        )

    def test_packaged_scaffold_resource_paths_follow_the_source_map(self) -> None:
        config = sync_generated.load(ROOT / ".agents/plugins/sources.json")
        for plugin, script in (("gpp", "new-gpp-project.sh"), ("msvc", "New-MsvcProject.ps1")):
            skill = {
                "identifier": f"{plugin}:scaffold",
                "name": "scaffold",
                "relative": f".agents/{plugin}/utility/scaffold/SKILL.md",
                "body": f"---\nname: scaffold\n---\n[script](../scripts/{script})\n<skill-directory>/../scripts/{script}",
            }
            name, body = sync_generated.package_body(skill, plugin, config["packages"][plugin], config["resources"])
            self.assertEqual("scaffold", name)
            self.assertIn(f"[script](../../resources/{plugin}/utility/scripts/{script})", body)
            self.assertIn(f"<skill-directory>/../../resources/{plugin}/utility/scripts/{script}", body)
            self.assertNotIn("../scripts/", body)

    def test_flat_adapters_keep_unique_names_and_resolve_canonical_sources(self) -> None:
        skill = {
            "name": "toolchain",
            "relative": ".agents/gpp/contract/toolchain/SKILL.md",
            "body": "---\nname: toolchain\ndescription: Example.\nkind: contract\ndomain: cpp\n---\n\n# Toolchain\n",
        }
        body = sync_generated.adapter_body(skill, ".codex/skills", "gpp-toolchain")
        self.assertIn("name: gpp-toolchain\n", body)
        self.assertIn("../../../.agents/gpp/contract/toolchain/SKILL.md", body)

    def test_mapping_validation_rejects_ambiguous_or_cross_scope_names(self) -> None:
        source = sync_generated.load(ROOT / ".agents/plugins/sources.json")
        payloads = sync_generated.load(ROOT / ".agents/plugins/payloads.json")
        scopes = {scope["plugin"]: scope["name"] for scope in source["scopes"]}
        skills = {
            identifier: {"name": identifier.split(":", 1)[1], "scope": scopes[identifier.split(":", 1)[0]]}
            for identifier in source["hostAdapterNames"]
        }
        mutations = (
            (lambda config: config["hostAdapterNames"].update({"gpp:toolchain": "msvc-toolchain"}), "unique valid flat"),
            (lambda config: config["packages"]["windows"]["skillNames"].update({"msvc:toolchain": "win32-style"}), "duplicate emitted skill name"),
            (lambda config: config["packages"]["cpp"]["compatibilitySkillAliases"]["cpp-style"].update({"source": "win32:style"}), "invalid compatibility skill alias"),
            (lambda config: config["packages"]["cpp"]["compatibilitySkillAliases"]["cpp-style"].update({"removeAfter": "2026-01-01"}), "must retain 2027-03-31"),
        )
        for mutate, message in mutations:
            config = copy.deepcopy(source)
            mutate(config)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                sync_generated.validate(ROOT, config, payloads, skills)


if __name__ == "__main__":
    unittest.main()
