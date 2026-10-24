"""Measures how much of the journal, supervisor and sync service packages the suite runs, the replays and the viewer tests apart, and fails under the floor: python3 scripts/coverage.py."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = "src/journal,src/supervisor,src/sync_service"
FLOOR_PERCENT = 95
# coverage and the test tools come from uv for this run alone, so nothing is installed into the project's Python
TOOLS = ("--with", "coverage", "--with", "pytest", "--with", "pytest-timeout")


def main() -> int:
    if shutil.which("uv") is None:
        print("measuring coverage needs uv, which fetches coverage.py for the run: https://docs.astral.sh/uv/", file=sys.stderr)
        return 2
    data = Path(tempfile.mkdtemp()) / "coverage.db"
    run = ["uv", "run", "--quiet", "--no-project", "--python", sys.executable, *TOOLS, "python", "-m", "coverage"]
    environment = {**os.environ, "COVERAGE_FILE": str(data)}
    subprocess.run([*run, "run", f"--source={PACKAGES}", "-m", "pytest", "-p", "no:warnings", "tests/"], cwd=ROOT, env=environment, check=False)
    return subprocess.run([*run, "report", f"--fail-under={FLOOR_PERCENT}", "--skip-covered", "--sort=miss"], cwd=ROOT, env=environment, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
