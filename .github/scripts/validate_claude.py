import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


VERSION_WARNING = 'No version specified. Consider adding a version following semver (e.g., "1.0.0")'


def validate_report(report, returncode):
    if not isinstance(report, dict) or type(report.get("success")) is not bool or report.get("strict") is not True:
        raise ValueError("invalid strict validation report")
    manifest = report.get("manifest")
    if not isinstance(manifest, dict) or not isinstance(report.get("contents"), list):
        raise ValueError("missing manifest or contents report")
    if not all(isinstance(manifest.get(key), list) for key in ("errors", "warnings")):
        raise ValueError("missing manifest issue lists")
    errors = []
    warnings = []

    def collect(value):
        if isinstance(value, dict):
            for key, entries in value.items():
                if key in ("errors", "warnings"):
                    if not isinstance(entries, list):
                        raise ValueError("invalid issue list")
                    for issue in entries:
                        if not isinstance(issue, dict) or not all(isinstance(issue.get(field), str) for field in ("path", "message")):
                            raise ValueError("invalid validation issue")
                        (errors if key == "errors" else warnings).append(issue)
                else:
                    collect(entries)
        elif isinstance(value, list):
            for entry in value:
                collect(entry)

    collect(report)
    expected_success = not errors and not warnings
    if report["success"] != expected_success or returncode != (0 if expected_success else 1):
        raise ValueError("validation status and exit code disagree with issues")
    unexpected = errors + [
        issue for issue in warnings
        if not (
            (issue["path"] == "version" or issue["path"].endswith("→ version"))
            and issue["message"] == VERSION_WARNING
        )
    ]
    return [f'{issue["path"]}: {issue["message"]}' for issue in unexpected]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    root = parser.parse_args().root.resolve()
    executable = shutil.which("claude")
    if executable is None:
        parser.error("claude is not on PATH")
    packages = json.loads((root / ".agents/plugins/sources.json").read_text(encoding="utf-8"))["packages"]
    targets = [root / ".claude-plugin/marketplace.json", *(root / "plugins" / name for name in packages)]
    problems = []
    for target in targets:
        try:
            result = subprocess.run(
                [executable, "plugin", "validate", "--strict", "--json", str(target)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
            )
            found = validate_report(json.loads(result.stdout), result.returncode)
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            found = [str(error)]
        problems.extend(f"{target}: {problem}" for problem in found)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"Claude validates the marketplace and all {len(packages)} versionless packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
