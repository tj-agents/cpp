import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CanonicalNameTests(unittest.TestCase):
    def test_only_canonical_packages_and_skills_are_published(self) -> None:
        expected = {
            "cpp": {
                "build",
                "style",
                "structure",
                "testing",
                "libraries",
                "direction",
                "learning",
                "domain-design",
                "mixins",
                "explanation",
            },
            "gpp": {"toolchain", "scaffold"},
            "msvc": {"toolchain", "scaffold"},
            "win32": {"style", "overview", "scaffold"},
        }
        payloads = json.loads((ROOT / ".agents/plugins/payloads.json").read_text())
        self.assertEqual({name: [name] for name in expected}, payloads["payloads"])
        self.assertNotIn("compatibilitySkillAliases", payloads)
        self.assertFalse((ROOT / ".agents/plugins/sources.json").exists())
        for plugin, names in expected.items():
            for source in (
                ROOT / f".agents/{plugin}/skills",
                ROOT / f"plugins/{plugin}/skills",
            ):
                self.assertEqual(
                    names, {p.parent.name for p in source.glob("*/SKILL.md")}
                )
            for host in ("codex", "claude"):
                for name in names:
                    body = (
                        ROOT / f".{host}/skills/{plugin}-{name}/SKILL.md"
                    ).read_text()
                    link = re.search(r"canonical definition\]\(([^)]+)\)", body)
                    self.assertIsNotNone(link)
                    assert link is not None
                    target = (
                        ROOT / f".{host}/skills/{plugin}-{name}" / link.group(1)
                    ).resolve()
                    self.assertEqual(
                        (ROOT / f".agents/{plugin}/skills/{name}/SKILL.md").resolve(),
                        target,
                    )
        for plugin in ("cpp", "win32"):
            self.assertTrue(
                (
                    ROOT / f"plugins/{plugin}/.agents/{plugin}/learning/knowledge.md"
                ).is_file()
            )

    def test_scaffold_resources_ship_with_canonical_and_native_entries(self) -> None:
        for plugin, script in (
            ("gpp", "new-gpp-project.sh"),
            ("msvc", "New-MsvcProject.ps1"),
            ("win32", "Add-Win32App.ps1"),
        ):
            canonical = ROOT / f".agents/{plugin}/skills/scaffold"
            for entry in (
                ROOT / f"plugins/{plugin}/.agents/{plugin}/skills/scaffold",
                ROOT / f"plugins/{plugin}/skills/scaffold",
                ROOT / f".codex/skills/{plugin}-scaffold",
                ROOT / f".claude/skills/{plugin}-scaffold",
            ):
                for source in canonical.rglob("*"):
                    if source.is_file() and source.name != "SKILL.md":
                        self.assertEqual(
                            source.read_bytes(),
                            (entry / source.relative_to(canonical)).read_bytes(),
                        )
            body = (canonical / "SKILL.md").read_text()
            self.assertIn(f"](scripts/{script})", body)
            self.assertIn(f"<skill-directory>/scripts/{script}", body)

    def test_every_host_manifest_names_the_canonical_repository(self) -> None:
        for host in ("claude", "codex"):
            for plugin in ("cpp", "gpp", "msvc", "win32"):
                manifest = json.loads(
                    (
                        ROOT / f".agents/plugins/manifests/{host}/{plugin}.json"
                    ).read_text()
                )
                self.assertEqual(
                    "https://github.com/tj-agents/cpp", manifest["repository"]
                )

    def test_no_generated_or_authored_file_is_git_ignored(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("Git is unavailable")
        files = [
            p.relative_to(ROOT).as_posix()
            for top in (".agents", ".claude", ".codex", "plugins")
            for p in (ROOT / top).rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        ]
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"],
            cwd=ROOT,
            input="\n".join(files),
            capture_output=True,
            text=True,
        )
        self.assertEqual("", result.stdout)
