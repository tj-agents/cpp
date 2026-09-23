import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("sync_generated", ROOT / ".agents/sync_generated.py")
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class PackageVersionTests(unittest.TestCase):
    def test_every_package_version_names_exactly_the_content_it_ships(self) -> None:
        recorded = json.loads((ROOT / SYNC.PACKAGE_VERSIONS).read_text(encoding="utf-8"))
        payloads = json.loads((ROOT / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))
        self.assertEqual(set(payloads["payloads"]), set(recorded))
        for package in sorted(payloads["payloads"]):
            version, digest = SYNC.package_state(ROOT, package)
            history = recorded[package]
            self.assertIn(
                version, history,
                f"{package} {version} is unrecorded: run `python .agents/sync_generated.py --record-package-versions`",
            )
            newest = max(history, key=lambda value: tuple(int(part) for part in value.split(".")))
            self.assertEqual(newest, version, f"{package} {version} is older than recorded {newest}")
            self.assertEqual(
                history[version], digest,
                f"{package} content changed without a version bump from {version}; bump both host manifests, "
                "regenerate, then record the new version",
            )


    def test_recorded_versions_are_never_rewritten(self) -> None:
        # Shallow CI checkouts have no main branch; local and merge-queue runs do.
        base = subprocess.run(
            ["git", "show", f"origin/main:{SYNC.PACKAGE_VERSIONS}"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if base.returncode != 0:
            self.skipTest("no published package-version record on origin/main")
        published = json.loads(base.stdout)
        current = json.loads((ROOT / SYNC.PACKAGE_VERSIONS).read_text(encoding="utf-8"))
        for package, history in published.items():
            for version, digest in history.items():
                recorded = current.get(package, {}).get(version)
                self.assertIsNotNone(recorded, f"{package} {version} is published on main but missing here; rebase onto main")
                self.assertEqual(digest, recorded, f"{package} {version} was rewritten")

    def test_digest_orders_files_by_case_sensitive_posix_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "plugins" / "sample"
            for relative, text in {"INDEX.md": "index", "hooks/a.py": "hook", "skills/x/SKILL.md": "skill"}.items():
                (package / relative).parent.mkdir(parents=True, exist_ok=True)
                (package / relative).write_bytes(text.encode())
            for host in ("claude", "codex"):
                (package / f".{host}-plugin").mkdir()
                (package / f".{host}-plugin/plugin.json").write_text('{"name": "sample", "version": "1.0.0"}')
            version, digest = SYNC.package_state(root, "sample")
            expected = hashlib.sha256()
            manifest = json.dumps({"name": "sample"}, sort_keys=True).encode()
            # Byte order: ".claude-plugin" < ".codex-plugin" < "INDEX.md" < "hooks" < "skills".
            for relative, data in (
                (".claude-plugin/plugin.json", manifest),
                (".codex-plugin/plugin.json", manifest),
                ("INDEX.md", b"index"),
                ("hooks/a.py", b"hook"),
                ("skills/x/SKILL.md", b"skill"),
            ):
                expected.update(relative.encode() + b"\0" + hashlib.sha256(data).digest())
            self.assertEqual(("1.0.0", expected.hexdigest()), (version, digest))


if __name__ == "__main__":
    unittest.main()
