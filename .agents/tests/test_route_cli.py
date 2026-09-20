import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / ".agents/gen_skill_routes.py"


class RouteCliTests(unittest.TestCase):
    def test_kind_and_layer_cannot_be_combined(self) -> None:
        result = subprocess.run([sys.executable, str(GENERATOR), "--kind", "gcc", "--layer", "windows", "--into", str(ROOT)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--kind and --layer cannot be combined", result.stderr)


if __name__ == "__main__":
    unittest.main()
