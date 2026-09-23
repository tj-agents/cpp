import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

import test_gpp_scaffold as gpp
import test_msvc_scaffold as msvc


ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "plugins" / "win32" / "resources" / "win32" / "utility" / "scripts" / "Add-Win32App.ps1"
LEGACY_OVERLAY = ROOT / "plugins" / "windows" / "resources" / "win32" / "utility" / "scripts" / "Add-Win32App.ps1"
LEGACY_MSVC = ROOT / "plugins" / "windows" / "resources" / "msvc" / "utility" / "scripts" / "New-MsvcProject.ps1"
GUI_SUBSYSTEM = 2


def pwsh(script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-File", str(script), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def snapshot(project: Path) -> dict[str, bytes]:
    return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}


def pe_subsystem(binary: Path) -> int:
    data = binary.read_bytes()
    header = struct.unpack_from("<I", data, 0x3C)[0]
    return struct.unpack_from("<H", data, header + 0x5C)[0]


class Win32ScaffoldTests(unittest.TestCase):
    def msvc_project(self, parent: Path, name: str, script: Path = msvc.SCRIPT) -> Path:
        created = pwsh(script, "-Name", name, "-Destination", str(parent))
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        return parent / name

    def gpp_project(self, parent: Path, name: str) -> Path:
        created = gpp.GppScaffoldTests().run_scaffold("--name", name, "--destination", str(parent))
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        return parent / name

    def convert(self, project: Path, script: Path = OVERLAY, *arguments: str) -> subprocess.CompletedProcess[str]:
        return pwsh(script, "-Project", str(project), *arguments)

    def test_overlay_changes_only_the_documented_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.msvc_project(Path(temporary), "gui-app")
            before = snapshot(project)
            converted = self.convert(project)
            self.assertEqual(0, converted.returncode, converted.stdout + converted.stderr)
            self.assertNotIn("Manual step", converted.stdout)
            after = snapshot(project)

            changed = {path for path in after if before.get(path) != after[path]}
            self.assertEqual(
                {
                    "app/CMakeLists.txt", "app/src/main.cpp", "app/app.manifest", "app/app.rc",
                    ".clang-tidy", ".clang-format", "AGENTS.md", "README.md", ".agents/skill-routes.json",
                },
                changed,
            )
            self.assertEqual(set(before), set(after) - {"app/app.manifest", "app/app.rc"})

            main = after["app/src/main.cpp"].decode()
            self.assertIn("int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int)", main)
            cmake = after["app/CMakeLists.txt"].decode()
            self.assertIn("add_executable(gui-app WIN32", cmake)
            self.assertIn("gui_app_sanitize", cmake)
            self.assertIn("UNICODE _UNICODE WIN32_LEAN_AND_MEAN NOMINMAX", cmake)
            manifest = after["app/app.manifest"].decode()
            for setting in ("PerMonitorV2", "Microsoft.Windows.Common-Controls", "<activeCodePage", "asInvoker", 'name="gui-app"'):
                self.assertIn(setting, manifest)
            tidy = after[".clang-tidy"].decode()
            self.assertIn("  -portability-avoid-pragma-once,\n  -cppcoreguidelines-pro-type-reinterpret-cast,", tidy)
            self.assertIn("  -readability-named-parameter\nWarningsAsErrors:", tidy)
            fmt = after[".clang-format"].decode()
            self.assertTrue(fmt.endswith("    Priority: 4\n...\n"), fmt)
            self.assertIn("'^<windows\\.h>$'", fmt)
            routes = json.loads(after[".agents/skill-routes.json"])
            self.assertEqual({"toolchain": "msvc", "apis": ["win32"]}, routes["profile"])

            if shutil.which("clang-format"):
                formatted = subprocess.run(
                    ["clang-format", "--dry-run", "-Werror", "app/src/main.cpp", "libs/core/src/core.cpp"],
                    cwd=project, capture_output=True, text=True,
                )
                self.assertEqual(0, formatted.returncode, formatted.stdout + formatted.stderr)

    def test_whatif_refusals_and_customized_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            project = self.msvc_project(parent, "preview")
            before = snapshot(project)
            preview = self.convert(project, OVERLAY, "-WhatIf")
            self.assertEqual(0, preview.returncode, preview.stdout + preview.stderr)
            self.assertEqual(before, snapshot(project))

            self.assertEqual(0, self.convert(project).returncode)
            again = self.convert(project)
            self.assertNotEqual(0, again.returncode)
            self.assertIn("is not the unmodified scaffold output", again.stdout + again.stderr)

            edited = self.msvc_project(parent, "edited")
            main = edited / "app/src/main.cpp"
            main.write_text(main.read_text(encoding="utf-8") + "// local change\n", encoding="utf-8")
            unchanged = snapshot(edited)
            refused = self.convert(edited)
            self.assertNotEqual(0, refused.returncode)
            self.assertEqual(unchanged, snapshot(edited))

            custom = self.msvc_project(parent, "custom")
            (custom / ".clang-tidy").write_text("Checks: '-*,modernize-*'\n", encoding="utf-8")
            converted = self.convert(custom)
            self.assertEqual(0, converted.returncode, converted.stdout + converted.stderr)
            self.assertIn("Manual step: .clang-tidy", converted.stdout)
            self.assertEqual("Checks: '-*,modernize-*'\n", (custom / ".clang-tidy").read_text(encoding="utf-8"))

    def test_gpp_projects_receive_the_gpp_win32_route_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.gpp_project(Path(temporary), "mingw-gui")
            converted = self.convert(project)
            self.assertEqual(0, converted.returncode, converted.stdout + converted.stderr)
            routes = json.loads((project / ".agents/skill-routes.json").read_text(encoding="utf-8"))
            self.assertEqual({"toolchain": "gpp", "apis": ["win32"]}, routes["profile"])
            self.assertEqual(["cpp", "gpp", "win32"], routes["layers"])

    def test_legacy_windows_package_converts_without_a_route_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.msvc_project(Path(temporary), "legacy", LEGACY_MSVC)
            self.assertFalse((project / ".agents").exists())
            converted = self.convert(project, LEGACY_OVERLAY)
            self.assertEqual(0, converted.returncode, converted.stdout + converted.stderr)
            self.assertTrue((project / "app/app.manifest").is_file())
            self.assertFalse((project / ".agents").exists())

    def test_gui_application_builds_with_real_msvc(self) -> None:
        if not msvc.VSWHERE.is_file() or not shutil.which("cmake") or not shutil.which("ninja"):
            self.skipTest("MSVC, CMake or Ninja not available")
        with tempfile.TemporaryDirectory() as temporary:
            project = self.msvc_project(Path(temporary), "msvcgui")
            self.assertEqual(0, self.convert(project).returncode)
            built = msvc.build_with_msvc(project)
            self.assertEqual(0, built.returncode, built.stdout + built.stderr)
            binary = project / "build/dev/bin/msvcgui.exe"
            self.assertEqual(GUI_SUBSYSTEM, pe_subsystem(binary))
            self.assertIn(b"PerMonitorV2", binary.read_bytes())
            self.assertEqual(0, subprocess.run([str(binary)]).returncode)

    def test_gui_application_builds_with_real_mingw(self) -> None:
        gxx = shutil.which("g++")
        if os.name != "nt" or not gxx or not shutil.which("cmake") or not shutil.which("ninja"):
            self.skipTest("MinGW g++, CMake or Ninja not available")
        with tempfile.TemporaryDirectory() as temporary:
            project = self.gpp_project(Path(temporary), "mingwgui")
            self.assertEqual(0, self.convert(project).returncode)
            configured = subprocess.run(
                ["cmake", "--preset", "gdb", f"-DCMAKE_CXX_COMPILER={gxx}", "-DBUILD_TESTING=OFF", "-DMINGWGUI_WARNINGS_AS_ERRORS=ON"],
                cwd=project, capture_output=True, text=True,
            )
            self.assertEqual(0, configured.returncode, configured.stdout + configured.stderr)
            built = subprocess.run(["cmake", "--build", "--preset", "gdb"], cwd=project, capture_output=True, text=True)
            self.assertEqual(0, built.returncode, built.stdout + built.stderr)
            binary = project / "build/gdb/bin/mingwgui.exe"
            self.assertEqual(GUI_SUBSYSTEM, pe_subsystem(binary))
            self.assertIn(b"PerMonitorV2", binary.read_bytes())
            self.assertEqual(0, subprocess.run([str(binary)]).returncode)


if __name__ == "__main__":
    unittest.main()
