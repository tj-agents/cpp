import argparse
import json
from pathlib import Path
import tempfile
import unittest

from test_selection_profiles import FIXTURES, ROOT, SelectionProfileTests, load_module, write_case


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reader", type=Path, required=True)
    args = parser.parse_args()
    reader = load_module("selection_parity_reader", args.reader.resolve(strict=True))
    metadata = json.loads((ROOT / ".agents/plugins/selection-profiles/cpp.json").read_text(encoding="utf-8"))
    candidates = ["cpp-agents/" + package for package in ("cpp", "gpp", "msvc", "win32")]
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SelectionProfileTests)
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        return 1
    for case in FIXTURES:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_case(root, case)
            result = reader.evaluate(metadata, "cpp-agents/cpp", candidates, root, case["files"])
        actual = (result["selected_ids"], result["selected_form"], bool(result["diagnostics"]))
        expected = (case["selected_ids"], case["selected_form"], case["invalid"])
        if actual != expected:
            raise AssertionError(f"{case['name']}: expected {expected!r}, received {result!r}")
    print(f"source hook and shared reader agree on {len(FIXTURES)} selection fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
