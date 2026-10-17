import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_claude", ROOT / ".github/scripts/validate_claude.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ClaudeValidationTests(unittest.TestCase):
    def setUp(self):
        self.warning = {"path": "version", "message": VALIDATOR.VERSION_WARNING, "code": None}
        self.report = {
            "success": False, "strict": True,
            "manifest": {"errors": [], "warnings": [copy.deepcopy(self.warning)]},
            "contents": [],
        }

    def test_accepts_native_missing_version_warning(self):
        self.assertEqual([], VALIDATOR.validate_report(self.report, 1))
        self.report["manifest"]["warnings"][0]["path"] = "plugins[0] plugin.json → version"
        self.assertEqual([], VALIDATOR.validate_report(self.report, 1))

    def test_accepts_clean_report(self):
        self.report["success"] = True
        self.report["manifest"]["warnings"] = []
        self.assertEqual([], VALIDATOR.validate_report(self.report, 0))

    def test_rejects_other_version_warnings(self):
        self.report["manifest"]["warnings"][0]["message"] = "Invalid version"
        self.assertTrue(VALIDATOR.validate_report(self.report, 1))

    def test_rejects_other_paths(self):
        self.report["manifest"]["warnings"][0]["path"] = "description"
        self.assertTrue(VALIDATOR.validate_report(self.report, 1))

    def test_rejects_errors_and_nested_content_warnings(self):
        for key in ("errors", "warnings"):
            with self.subTest(key=key):
                self.report["contents"] = [{key: [{"path": "skills/example", "message": "Invalid skill"}]}]
                self.assertTrue(VALIDATOR.validate_report(self.report, 1))

    def test_rejects_status_disagreement(self):
        for success, returncode in ((True, 0), (False, 0), (False, 2), (1, 1)):
            with self.subTest(success=success, returncode=returncode):
                self.report["success"] = success
                with self.assertRaises(ValueError):
                    VALIDATOR.validate_report(self.report, returncode)

    def test_rejects_incomplete_reports(self):
        for invalid in ({}, [], {**self.report, "manifest": {}}, {**self.report, "contents": None}, {**self.report, "strict": False}):
            with self.subTest(report=invalid), self.assertRaises(ValueError):
                VALIDATOR.validate_report(invalid, 1)

    def test_rejects_malformed_issue_lists(self):
        for invalid in (None, {}, [None], [{}], [{"path": "version", "message": None}]):
            with self.subTest(issues=invalid), self.assertRaises(ValueError):
                self.report["manifest"]["warnings"] = invalid
                VALIDATOR.validate_report(self.report, 1)


if __name__ == "__main__":
    unittest.main()
