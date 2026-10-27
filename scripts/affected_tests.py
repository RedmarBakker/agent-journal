"""Prints the tests that cover the files it is handed, one a line, read from the coverage map python3 scripts/suite.py --coverage-map writes: each handed test file, and each test that ran a handed source file, the quickest by the suite's last seconds first and at most MOST_TESTS of them. Set as workers.affected_tests_command, the journal hands it a worker's changed files at clock-out and runs what the worker did not name."""
import json
import re
import subprocess
import sys
from pathlib import Path

# the most tests it names, so a change to a file every test runs never turns a clock-out into the whole suite
MOST_TESTS = 60
TEST_FILE = re.compile(r"^tests/(.+/)?test_[^/]+\.py$")


def main(changed: list[str]) -> int:
    runtime = checkout() / ".journal" / "runtime"
    coverage_map, durations = runtime / "test-coverage.json", runtime / "suite-durations.json"
    covered = json.loads(coverage_map.read_text()) if coverage_map.is_file() else {}
    seconds = json.loads(durations.read_text()) if durations.is_file() else {}
    print("\n".join(affected(changed, covered, seconds)))
    return 0


def checkout() -> Path:
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True, timeout=10).stdout.strip()
    return Path(common).parent


def affected(changed: list[str], covered: dict[str, list[str]], seconds: dict[str, float]) -> list[str]:
    test_files = [path for path in changed if TEST_FILE.match(path)]
    sources = set(changed) - set(test_files)
    running = sorted((node for node, files in covered.items() if sources.intersection(files) and node.split("::")[0] not in test_files), key=lambda node: seconds.get(node, 0.0))
    return [*test_files, *running][:MOST_TESTS]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
