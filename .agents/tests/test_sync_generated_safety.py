import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "scaffold_routes", ROOT / "scripts/gen_skill_routes.py"
)
assert SPEC is not None and SPEC.loader is not None
ROUTES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ROUTES)


class ScaffoldPreparationTests(unittest.TestCase):
    def test_repository_assets_are_current(self) -> None:
        self.assertEqual(0, ROUTES.prepare_scaffolds(ROOT, True))

    def test_preparation_detects_and_repairs_missing_modified_and_extra_assets(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shared = root / ".agents/cpp/assets/scaffold/templates"
            shared.mkdir(parents=True)
            (shared / "hidden.in").write_bytes(b"shared\r\n")
            self.assertEqual(1, ROUTES.prepare_scaffolds(root, True))
            self.assertEqual(0, ROUTES.prepare_scaffolds(root, False))
            self.assertEqual(0, ROUTES.prepare_scaffolds(root, True))
            assets = root / ".agents/gpp/skills/scaffold/assets/shared/templates"
            self.assertEqual(b"shared\r\n", (assets / "hidden.in").read_bytes())
            (assets / "hidden.in").write_bytes(b"modified")
            extra = assets / "obsolete.in"
            extra.write_bytes(b"obsolete")
            own = root / ".agents/gpp/skills/scaffold/assets/templates/owned.in"
            own.write_bytes(b"owned")
            self.assertEqual(1, ROUTES.prepare_scaffolds(root, True))
            self.assertEqual(0, ROUTES.prepare_scaffolds(root, False))
            self.assertFalse(extra.exists())
            self.assertEqual(b"owned", own.read_bytes())
            (shared / "hidden.in").unlink()
            self.assertEqual(1, ROUTES.prepare_scaffolds(root, True))
            self.assertEqual(0, ROUTES.prepare_scaffolds(root, False))
            self.assertFalse((assets / "hidden.in").exists())

    def test_preparation_refuses_a_redirected_owned_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shared = root / ".agents/cpp/assets/scaffold/templates"
            shared.mkdir(parents=True)
            (shared / "owned.in").write_bytes(b"shared")
            authored = root / "authored"
            authored.mkdir()
            protected = authored / "owned.in"
            protected.write_bytes(b"authored")
            redirected = root / ".agents/gpp/skills/scaffold/assets/shared/templates"
            redirected.parent.mkdir(parents=True)
            if os.name == "nt":
                command = f'cmd.exe /d /s /c mklink /J "{redirected}" "{authored}"'
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=10
                )
                self.assertEqual(0, result.returncode, result.stderr)
            else:
                redirected.symlink_to(authored, target_is_directory=True)
            try:
                with self.assertRaisesRegex(ValueError, "escapes its owned root"):
                    ROUTES.prepare_scaffolds(root, False)
                self.assertEqual(b"authored", protected.read_bytes())
            finally:
                if os.name == "nt":
                    redirected.rmdir()
                else:
                    redirected.unlink()

    def test_six_profiles_preserve_toolchain_and_api_independence(self) -> None:
        assets = ROUTES.scaffold_assets(ROOT)
        for toolchain in ("gpp", "msvc"):
            console = (
                ROOT
                / f".agents/{toolchain}/skills/scaffold/assets/templates"
                / ".agents/skill-routes.json.in"
            )
            self.assertEqual(ROUTES.rendered(toolchain).encode(), assets[console])
            profile = (
                ROOT / f".agents/win32/skills/scaffold/assets/routes/{toolchain}.json"
            )
            original = (
                ROOT
                / ".agents/win32/skills/scaffold/assets/routes/console"
                / f"{toolchain}.json"
            )
            self.assertEqual(
                ROUTES.rendered(toolchain, ["win32"]).encode(), assets[profile]
            )
            self.assertEqual(assets[console], assets[original])
            self.assertIn(
                f"{toolchain}:toolchain",
                ROUTES.skills_for(toolchain, ["win32"], "app/main.cpp"),
            )
            self.assertNotIn(
                f"{'msvc' if toolchain == 'gpp' else 'gpp'}:toolchain",
                ROUTES.skills_for(toolchain, ["win32"], "app/main.cpp"),
            )
