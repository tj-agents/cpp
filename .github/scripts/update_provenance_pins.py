"""Propose exact consumer Git-object pins without executing consumer-owned code."""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlencode


REPOSITORY = "tj-agents/cpp"
ATTESTER = ".agents/attest-external-contract.ps1"
GATE = ".github/workflows/provenance-gate.yml"
TRUST_TOOLS = (ATTESTER, GATE, ".github/scripts/update_provenance_pins.py",
               ".github/workflows/update-provenance-pins.yml")
PIN_TYPES = {
    ".agents/plugins/skill-contract.json": "blob",
    ".agents/tests/test_attester_safety.py": "blob",
    ".agents/tests/test_marketplace_contract.py": "blob",
    ".github/workflows/attester-safety.yml": "blob",
    ".github/workflows/ci.yml": "blob",
    "contracts": "tree",
}
PIN_BLOCK = re.compile(r"(?m)^\$expectedCandidateObjects = \[ordered\]@\{\r?\n(?P<entries>.*?)^\}", re.S)
PIN_ENTRY = re.compile(r'    "([^"\r\n]+)" = "([0-9a-f]{40})"')
SHA = re.compile(r"[0-9a-f]{40}")


class UpdateError(Exception):
    pass


class TrustRootChange(UpdateError):
    def __init__(self, number, head, main):
        super().__init__("Consumer trust tools differ from main; synchronize an ordinary consumer or use the dedicated manual bootstrap for intentional root changes")
        self.record = {"repository": REPOSITORY, "consumer_pr": number, "consumer_head": head,
                       "base": main, "manual_bootstrap": True, "reason": str(self)}


class GitHub:
    def __init__(self):
        self.executable = shutil.which("gh")
        if self.executable is None:
            raise UpdateError("GitHub CLI is required")

    def api(self, endpoint, *, method="GET", body=None, missing_ok=False):
        command = [self.executable, "api", f"repos/{REPOSITORY}/{endpoint}", "--method", method]
        if body is not None:
            command.extend(["--input", "-"])
        result = subprocess.run(command, input=json.dumps(body) if body is not None else None,
                                capture_output=True, text=True, encoding="utf-8", check=False)
        if result.returncode:
            if missing_ok and "(HTTP 404)" in result.stderr:
                return None
            raise UpdateError(f"GitHub {method} {endpoint} failed: {result.stderr.strip()}")
        return json.loads(result.stdout)


def require_sha(value):
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise UpdateError("Expected a full lowercase Git commit/object SHA")
    return value


def object_inventory(api, commit):
    tree = api.api(f"git/commits/{require_sha(commit)}")["tree"]["sha"]
    result = api.api(f"git/trees/{require_sha(tree)}?recursive=1")
    if result.get("truncated") is not False:
        raise UpdateError("Git tree inventory is incomplete")
    return tree, {item["path"]: item for item in result["tree"]}


def object_sha(inventory, path, kind):
    item = inventory.get(path, {})
    expected_mode = "040000" if kind == "tree" else "100644"
    if item.get("type") != kind or item.get("mode") != expected_mode:
        raise UpdateError(f"Missing or unexpected object type/mode: {path}")
    return require_sha(item.get("sha"))


def read_pins(source):
    blocks = list(PIN_BLOCK.finditer(source))
    if len(blocks) != 1:
        raise UpdateError("Expected exactly one approved candidate-object map")
    entries = blocks[0].group("entries").splitlines()
    matches = [PIN_ENTRY.fullmatch(line) for line in entries]
    if any(match is None for match in matches):
        raise UpdateError("Unexpected candidate-object map format")
    pins = {match[1]: match[2] for match in matches}
    if len(pins) != len(entries) or set(pins) != set(PIN_TYPES):
        raise UpdateError("Approved candidate-object inventory changed; review the updater first")
    return blocks[0], pins


def replace_pins(source, objects):
    block, _ = read_pins(source)
    newline = "\r\n" if "\r\n" in block[0] else "\n"
    entries = newline.join(f'    "{path}" = "{objects[path]}"' for path in PIN_TYPES)
    return source[:block.start("entries")] + entries + newline + source[block.end("entries"):]


def read_blob(api, blob_id):
    blob = api.api(f"git/blobs/{require_sha(blob_id)}")
    if blob.get("encoding") != "base64":
        raise UpdateError("Expected a base64 attester blob")
    content = base64.b64decode(blob["content"])
    actual = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    if actual != blob_id:
        raise UpdateError("Attester bytes do not match the trusted Git object")
    return content.decode("utf-8")


def open_proposals(api, branch):
    query = urlencode({"state": "open", "base": "main", "head": f"tj-agents:{branch}"})
    return api.api(f"pulls?{query}")


def check_generated_branch(api, previous, commit, record, bot_login):
    if (commit.get("author") or {}).get("login") != bot_login:
        raise UpdateError("Update branch contains a head from another author; preserve it")
    parent = require_sha(commit["parents"][0]["sha"])
    reachable = api.api(f"compare/{parent}...{record['base']}")
    if (reachable["base_commit"]["sha"] != parent or reachable["merge_base_commit"]["sha"] != parent
            or reachable["status"] not in ("ahead", "identical")):
        raise UpdateError("Update branch has an unrecognized base; preserve it")
    comparison = api.api(f"compare/{parent}...{previous}")
    files = comparison.get("files", [])
    if (len(files) != 1 or files[0]["filename"] != ATTESTER or files[0]["status"] != "modified"):
        raise UpdateError("Update branch contains unexpected file changes; preserve it")
    baseline = api.api(f"contents/{ATTESTER}?ref={parent}")["sha"]
    original = read_blob(api, baseline)
    changed = read_blob(api, files[0]["sha"])
    masked = {path: "0" * 40 for path in PIN_TYPES}
    if replace_pins(original, masked) != replace_pins(changed, masked):
        raise UpdateError("Update branch contains edits outside generated pin values; preserve it")


def proposal(api, number, expected_head=None, expected_main=None):
    if type(number) is not int or number < 1:
        raise UpdateError("Consumer PR must be a positive integer")
    pull = api.api(f"pulls/{number}")
    if (pull["state"] != "open" or pull["head"]["repo"]["full_name"] != REPOSITORY
            or pull["base"]["repo"]["full_name"] != REPOSITORY or pull["base"]["ref"] != "main"
            or pull["head"]["ref"].startswith("Chore/ProvenancePins-")):
        raise UpdateError("Expected an open canonical consumer PR targeting main")
    head = require_sha(pull["head"]["sha"])
    if expected_head and head != require_sha(expected_head):
        raise UpdateError("Consumer head moved; use the latest workflow event")
    main = require_sha(api.api("git/ref/heads/main")["object"]["sha"])
    if expected_main and main != require_sha(expected_main):
        raise UpdateError("Trusted checkout is behind main; rerun the workflow")
    base_tree, base_objects = object_inventory(api, main)
    _, candidate_objects = object_inventory(api, head)
    for path in TRUST_TOOLS:
        if object_sha(base_objects, path, "blob") != object_sha(candidate_objects, path, "blob"):
            raise TrustRootChange(number, head, main)
    blob_id = object_sha(base_objects, ATTESTER, "blob")
    source = read_blob(api, blob_id)
    _, old = read_pins(source)
    new = {path: object_sha(candidate_objects, path, kind) for path, kind in PIN_TYPES.items()}
    updates = {path: {"old": old[path], "new": new[path]} for path in PIN_TYPES if old[path] != new[path]}
    record = {"repository": REPOSITORY, "consumer_pr": number, "consumer_head": head,
              "base": main, "branch": f"Chore/ProvenancePins-{number}", "updates": updates}
    return record, replace_pins(source, new), base_tree


def pr_body(record):
    rows = "\n".join(f"| {path} | {item['old']} | {item['new']} |" for path, item in record["updates"].items())
    return (
        f"## Why\n\nConsumer #{record['consumer_pr']} at {record['consumer_head']} changes protected objects "
        "whose approved pins differ from canonical main.\n\n## What\n\n"
        "Update only the approved candidate-object values in the trusted attester. "
        "The objects were read as Git data; consumer code was never executed.\n\n"
        f"| Path | Previous object | Proposed object |\n|---|---|---|\n{rows}\n\n"
        "## Review and acceptance\n\n"
        "- [ ] Independently review the complete changed objects and this dedicated trust-root update.\n"
        "- [ ] Confirm exact-head ordinary CI and attester-safety checks pass.\n"
        "- [ ] Land through the documented PROVENANCE_GATE.md bootstrap procedure.\n"
        "- [ ] Incorporate the landed attester into the consumer, freeze its new head and obtain successful provenance.\n\n"
        f"Generated from main {record['base']}. The human-gate label retains maintainer review. "
        "This proposal neither authenticates the private producer nor issues an attestation.\n"
    )


def publish(api, saved, bot_login):
    if not re.fullmatch(r"[A-Za-z0-9-]+\[bot\]", bot_login or ""):
        raise UpdateError("Publishing requires the configured GitHub App bot login")
    record, source, base_tree = proposal(api, saved["consumer_pr"], saved["consumer_head"])
    if record != saved:
        raise UpdateError("Main or proposal changed; generate a fresh proposal")
    branch = record["branch"]
    pulls = open_proposals(api, branch)
    if len(pulls) > 1 or any(pull["user"]["login"] != bot_login for pull in pulls):
        raise UpdateError("Update branch already has a different PR owner")
    if pulls and pulls[0].get("draft") is not True:
        raise UpdateError("Update PR is ready for review; preserve its frozen head and body")
    if not record["updates"] and not pulls:
        return None
    existing = api.api(f"git/ref/heads/{branch}", missing_ok=True)
    if pulls and existing is None:
        raise UpdateError("Existing update PR has no branch; preserve it for reconciliation")
    if existing:
        previous = require_sha(existing["object"]["sha"])
        commit = api.api(f"commits/{previous}")
        check_generated_branch(api, previous, commit, record, bot_login)
    if not record["updates"]:
        pull = api.api(f"pulls/{pulls[0]['number']}", method="PATCH", body={"state": "closed", "body":
            pulls[0]["body"] + f"\n## Superseded\n\nConsumer {record['consumer_head']} now matches the approved pins; closed the obsolete draft.\n"})
        return pull["html_url"]
    blob = api.api("git/blobs", method="POST", body={"content": source, "encoding": "utf-8"})
    tree = api.api("git/trees", method="POST", body={"base_tree": base_tree, "tree": [
        {"path": ATTESTER, "mode": "100644", "type": "blob", "sha": blob["sha"]}]})
    if not existing or commit["commit"]["tree"]["sha"] != tree["sha"]:
        parents = list(dict.fromkeys([record["base"], previous] if existing else [record["base"]]))
        created = api.api("git/commits", method="POST", body={
            "message": f"Update provenance pins for consumer #{record['consumer_pr']} at {record['consumer_head']}",
            "tree": tree["sha"], "parents": parents})
        if existing:
            api.api(f"git/refs/heads/{branch}", method="PATCH", body={"sha": created["sha"], "force": False})
        else:
            api.api("git/refs", method="POST", body={"ref": f"refs/heads/{branch}", "sha": created["sha"]})
    details = {"title": f"Update provenance pins for consumer #{record['consumer_pr']}", "body": pr_body(record)}
    if pulls:
        pull = pulls[0]
        if any(pull.get(key) != value for key, value in details.items()):
            pull = api.api(f"pulls/{pull['number']}", method="PATCH", body=details)
    else:
        pull = api.api("pulls", method="POST", body={**details, "base": "main", "head": branch, "draft": True})
    if "human-gate" not in {label["name"] for label in pull.get("labels", [])}:
        api.api(f"issues/{pull['number']}/labels", method="POST", body={"labels": ["human-gate"]})
    return pull["html_url"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int)
    parser.add_argument("--expected-head")
    parser.add_argument("--trusted-main")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--publish", type=Path, metavar="PROPOSAL")
    parser.add_argument("--bot-login")
    args = parser.parse_args()
    try:
        api = GitHub()
        if args.publish:
            print(publish(api, json.loads(args.publish.read_text(encoding="utf-8")), args.bot_login) or "No pin changes")
        else:
            try:
                record, _, _ = proposal(api, args.pr, args.expected_head, args.trusted_main)
            except TrustRootChange as error:
                record = error.record
            rendered = json.dumps(record, indent=2) + "\n"
            if args.output:
                args.output.write_text(rendered, encoding="utf-8")
            print(rendered, end="")
            if os.environ.get("GITHUB_OUTPUT"):
                needs_publish = (not record.get("manual_bootstrap") and
                                 (bool(record["updates"]) or bool(open_proposals(api, record["branch"]))))
                with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                    output.write(f"needs_publish={str(needs_publish).lower()}\n")
    except (UpdateError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"Provenance update failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
