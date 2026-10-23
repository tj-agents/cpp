import base64
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("pin_updates", ROOT / ".github/scripts/update_provenance_pins.py")
updates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updates)
BOT = "tj-agents-test[bot]"


def git_blob(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


class FakeGitHub:
    """An in-memory GitHub Git-data/PR service; never launches candidate code."""

    def __init__(self):
        self.main = "a" * 40
        self.head = "b" * 40
        self.source = (ROOT / updates.ATTESTER).read_bytes()
        _, pins = updates.read_pins(self.source.decode())
        objects = {}
        for path, kind in updates.PIN_TYPES.items():
            objects[path] = {"path": path, "sha": pins[path], "type": kind,
                             "mode": "040000" if kind == "tree" else "100644"}
        for path in updates.TRUST_TOOLS:
            objects[path] = {"path": path, "sha": git_blob(self.source if path == updates.ATTESTER else path.encode()),
                             "type": "blob", "mode": "100644"}
        self.base_objects = objects
        self.candidate_objects = deepcopy(objects)
        for path in (".agents/tests/test_marketplace_contract.py", ".github/workflows/ci.yml"):
            self.candidate_objects[path]["sha"] = git_blob(f"changed {path}".encode())
        self.consumer = {"number": 42, "state": "open", "head": {
            "repo": {"full_name": updates.REPOSITORY}, "ref": "Feature/Consumer", "sha": self.head},
            "base": {"repo": {"full_name": updates.REPOSITORY}, "ref": "main"}}
        self.truncated = False
        self.ref = None
        self.branch_author = BOT
        self.commits = {}
        self.pulls = []
        self.writes = []

    def api(self, endpoint, *, method="GET", body=None, missing_ok=False):
        if method != "GET":
            self.writes.append((method, endpoint, deepcopy(body)))
        if endpoint == "pulls/42":
            return deepcopy(self.consumer)
        if endpoint == "git/ref/heads/main":
            return {"object": {"sha": self.main}}
        if endpoint == f"git/commits/{self.main}":
            return {"tree": {"sha": "c" * 40}}
        if endpoint == f"git/commits/{self.head}":
            return {"tree": {"sha": "d" * 40}}
        if endpoint in (f"git/trees/{'c' * 40}?recursive=1", f"git/trees/{'d' * 40}?recursive=1"):
            inventory = self.base_objects if "/" + "c" * 40 in endpoint else self.candidate_objects
            return {"truncated": self.truncated, "tree": list(deepcopy(inventory).values())}
        if endpoint == f"git/blobs/{git_blob(self.source)}":
            return {"encoding": "base64", "content": base64.b64encode(self.source).decode()}
        if endpoint.startswith("git/ref/heads/Chore/"):
            return {"object": {"sha": self.ref}} if self.ref else None
        if endpoint.startswith("pulls?"):
            return deepcopy(self.pulls)
        if endpoint.startswith("commits/"):
            return {"author": {"login": self.branch_author},
                    "commit": {"tree": {"sha": self.commits[self.ref]["tree"]}}}
        if endpoint in ("git/blobs", "git/trees"):
            return {"sha": git_blob(json.dumps(body, sort_keys=True).encode())}
        if endpoint == "git/commits":
            sha = git_blob(json.dumps(body, sort_keys=True).encode())
            self.commits[sha] = deepcopy(body)
            return {"sha": sha}
        if endpoint == "git/refs" or endpoint.startswith("git/refs/heads/"):
            if self.ref and self.ref not in self.commits[body["sha"]]["parents"]:
                raise AssertionError("Expected a fast-forward update preserving the existing head")
            self.ref = body["sha"]
            return {}
        if endpoint == "pulls":
            self.pulls = [{**deepcopy(body), "number": 51, "user": {"login": BOT}, "labels": [],
                           "html_url": "https://github.com/tj-agents/cpp/pull/51"}]
            return deepcopy(self.pulls[0])
        if endpoint == "pulls/51":
            self.pulls[0].update(deepcopy(body))
            return deepcopy(self.pulls[0])
        if endpoint == "issues/51/labels":
            self.pulls[0]["labels"] = [{"name": name} for name in body["labels"]]
            return deepcopy(self.pulls[0]["labels"])
        raise AssertionError((method, endpoint, body, missing_ok))


class PinUpdateTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeGitHub()

    def test_exact_objects_and_only_pin_values_change(self):
        record, source, _ = updates.proposal(self.api, 42, self.api.head, self.api.main)
        self.assertEqual(2, len(record["updates"]))
        old = self.api.source.decode()
        restored = source
        for item in record["updates"].values():
            restored = restored.replace(item["new"], item["old"])
        self.assertEqual(old, restored)
        self.assertEqual([], self.api.writes)

    def test_unchanged_consumer_needs_no_pr_or_writes(self):
        self.api.candidate_objects = deepcopy(self.api.base_objects)
        record, _, _ = updates.proposal(self.api, 42)
        self.assertEqual({}, record["updates"])
        self.assertIsNone(updates.publish(self.api, record, BOT))
        self.assertEqual([], self.api.writes)

    def test_rejects_forks_closed_or_wrong_base_before_publishing(self):
        for section, field, value in (("head", "repo", {"full_name": "other/cpp"}),
                                      ("base", "ref", "other"), (None, "state", "closed")):
            with self.subTest(field=field, value=value):
                api = FakeGitHub()
                target = api.consumer[section] if section else api.consumer
                target[field] = value
                with self.assertRaises(updates.UpdateError):
                    updates.proposal(api, 42)
                self.assertEqual([], api.writes)

    def test_rejects_stale_consumer_or_checkout(self):
        with self.assertRaisesRegex(updates.UpdateError, "Consumer head moved"):
            updates.proposal(self.api, 42, "e" * 40)
        with self.assertRaisesRegex(updates.UpdateError, "behind main"):
            updates.proposal(self.api, 42, expected_main="e" * 40)
        self.assertEqual([], self.api.writes)

    def test_rejects_changed_trust_tools_truncated_trees_and_symlinks(self):
        for path in updates.TRUST_TOOLS:
            with self.subTest(path=path):
                api = FakeGitHub()
                api.candidate_objects[path]["sha"] = "e" * 40
                with self.assertRaisesRegex(updates.UpdateError, "trust tools differ"):
                    updates.proposal(api, 42)
                self.assertEqual([], api.writes)
        self.api.truncated = True
        with self.assertRaisesRegex(updates.UpdateError, "incomplete"):
            updates.proposal(self.api, 42)
        self.api.truncated = False
        self.api.candidate_objects[".github/workflows/ci.yml"]["mode"] = "120000"
        with self.assertRaisesRegex(updates.UpdateError, "type/mode"):
            updates.proposal(self.api, 42)

    def test_unknown_or_duplicate_pin_inventory_fails_closed(self):
        source = self.api.source.decode()
        for broken in (source.replace('    "contracts"', '    "other"'),
                       source + source, source.replace('    "contracts"', '    "contracts" = "' + "a" * 40 + '"\n    "contracts"')):
            with self.subTest():
                with self.assertRaises(updates.UpdateError):
                    updates.read_pins(broken)

    def test_publish_creates_one_draft_and_identical_repeat_reuses_it(self):
        record, _, _ = updates.proposal(self.api, 42)
        first = updates.publish(self.api, record, BOT)
        first_head = self.api.ref
        self.assertTrue(self.api.pulls[0]["draft"])
        self.assertIn("## Why", self.api.pulls[0]["body"])
        self.assertIn("## What", self.api.pulls[0]["body"])
        self.assertEqual([{"name": "human-gate"}], self.api.pulls[0]["labels"])
        self.api.writes.clear()
        self.assertEqual(first, updates.publish(self.api, record, BOT))
        self.assertEqual(first_head, self.api.ref)
        self.assertEqual(1, len(self.api.commits))
        self.assertEqual(["git/blobs", "git/trees"], [endpoint for _, endpoint, _ in self.api.writes])

    def test_changed_proposal_reuses_pr_and_fast_forwards_bot_branch(self):
        saved, _, _ = updates.proposal(self.api, 42)
        updates.publish(self.api, saved, BOT)
        previous = self.api.ref
        self.api.candidate_objects[".github/workflows/ci.yml"]["sha"] = "e" * 40
        changed, _, _ = updates.proposal(self.api, 42)
        updates.publish(self.api, changed, BOT)
        self.assertEqual(1, len(self.api.pulls))
        self.assertNotEqual(previous, self.api.ref)
        self.assertIn(previous, self.api.commits[self.api.ref]["parents"])
        patches = [body for method, endpoint, body in self.api.writes
                   if method == "PATCH" and endpoint.startswith("git/refs/")]
        self.assertEqual(False, patches[-1]["force"])

    def test_changed_main_or_foreign_branch_owner_blocks_all_writes(self):
        saved, _, _ = updates.proposal(self.api, 42)
        self.api.main = "e" * 40
        with self.assertRaisesRegex(updates.UpdateError, "Main or proposal changed"):
            updates.publish(self.api, saved, BOT)
        self.assertEqual([], self.api.writes)
        self.api.main = saved["base"]
        updates.publish(self.api, saved, BOT)
        self.api.branch_author = "someone-else"
        self.api.writes.clear()
        with self.assertRaisesRegex(updates.UpdateError, "another author"):
            updates.publish(self.api, saved, BOT)
        self.assertEqual([], self.api.writes)


if __name__ == "__main__":
    unittest.main()
