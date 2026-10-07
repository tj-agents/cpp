import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = json.loads((ROOT / ".agents/tests/fixtures/selection_profiles.json").read_text(encoding="utf-8"))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HOOK = load_module("selection_source_hook", ROOT / ".agents/hooks/session_context.py")
SYNC = load_module("selection_source_sync", ROOT / ".agents/sync_generated.py")


def write_case(root, case):
    if case["document"] is not None:
        path = root / HOOK.ROUTES_FILE
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(case["document"]), encoding="utf-8")
    for relative in case["files"]:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")


class SelectionProfileTests(unittest.TestCase):
    def test_source_hook_matches_shared_fixture_corpus(self):
        for case in FIXTURES:
            with self.subTest(case=case["name"]), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                write_case(root, case)
                profile = HOOK.declared_profile(root)
                expected = case["profile"]
                self.assertEqual(None if expected is None else (expected[0], frozenset(expected[1])), profile)
                with mock.patch.object(HOOK, "tracked_project", return_value=(root, case["files"])), mock.patch.object(HOOK, "is_native_windows", return_value=False):
                    context = HOOK.context_for(root)
                ids = []
                for package, message in (("cpp", HOOK.CPP_CONTEXT), ("gpp", HOOK.GPP_CONTEXT), ("msvc", HOOK.MSVC_CONTEXT), ("win32", HOOK.WIN32_CONTEXT)):
                    if message in context:
                        ids.append("cpp-agents/" + package)
                self.assertEqual(case["selected_ids"], sorted(ids))

    def test_profile_is_shipped_only_by_canonical_owner(self):
        output, config = SYNC.build(ROOT)
        paths = [path for path in output if path.endswith("/selection-profile.json")]
        self.assertEqual(["plugins/cpp/selection-profile.json"], paths)
        source = ROOT / config["selection_profiles"]["cpp"]["source"]
        self.assertEqual(source.read_bytes(), output[paths[0]])
        self.assertEqual(source.read_bytes(), (ROOT / paths[0]).read_bytes())

    def test_generator_rejects_remapped_or_noncanonical_owners(self):
        config = json.loads((ROOT / ".agents/plugins/sources.json").read_text(encoding="utf-8"))
        for field, value in (("source", "../profile.json"), ("destination", "../profile.json")):
            changed = copy.deepcopy(config)
            changed["selection_profiles"]["cpp"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                SYNC.selection_profile_sources(ROOT, changed)
        changed = copy.deepcopy(config)
        changed["selection_profiles"]["base"] = changed["selection_profiles"].pop("cpp")
        with self.assertRaises(ValueError):
            SYNC.selection_profile_sources(ROOT, changed)

    def test_generator_rejects_bad_json_identity(self):
        config = json.loads((ROOT / ".agents/plugins/sources.json").read_text(encoding="utf-8"))
        for document in ([], {"owner_package": "cpp-agents/base", "schema_version": 1}, {"owner_package": "cpp-agents/cpp", "schema_version": True}):
            with self.subTest(document=document), mock.patch.object(SYNC, "load", return_value=document), self.assertRaises(ValueError):
                SYNC.selection_profile_sources(ROOT, config)


if __name__ == "__main__":
    unittest.main()
