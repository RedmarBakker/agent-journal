"""Runs the test suite: a run naming tests or options is one pytest run; the whole suite is split into shards run side by side, one per core but two, and their outcomes added up."""
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTEST = [sys.executable, "-m", "pytest", "-p", "no:warnings"]
SHARD_VARIABLE = "JOURNAL_TEST_SHARD"
SPARE_CORES = 2
MOST_SHARDS = 8
SHARD_TIMEOUT_SECONDS = 600
COUNTS = re.compile(r"(\d+) (passed|failed|errors?|skipped|deselected|xfailed|xpassed)")
FAILURE_START = re.compile(r"^(=+ (FAILURES|ERRORS) =+|_{3,} .+ _{3,})$")
SUMMARY_START = re.compile(r"^=+ short test summary info =+$")


def shard_count() -> int:
    return max(1, min(MOST_SHARDS, (os.cpu_count() or 2) - SPARE_CORES))


def started(index: int, count: int, folder: Path) -> tuple[subprocess.Popen, Path]:
    output = folder / f"shard-{index}.txt"
    process = subprocess.Popen(PYTEST, cwd=ROOT, env={**os.environ, SHARD_VARIABLE: f"{index}/{count}"}, stdout=output.open("w"), stderr=subprocess.STDOUT)
    return process, output


def outcome(text: str) -> dict[str, int]:
    last = next((line for line in reversed(text.splitlines()) if COUNTS.search(line) and " in " in line), "")
    counts: dict[str, int] = {}
    for number, word in COUNTS.findall(last):
        name = "errors" if word.startswith("error") else word
        counts[name] = counts.get(name, 0) + int(number)
    return counts


def failure_lines(text: str) -> list[str]:
    lines, keeping = [], False
    for line in text.splitlines():
        if FAILURE_START.match(line) or SUMMARY_START.match(line):
            keeping = True
        if keeping and COUNTS.search(line) and " in " in line and line.startswith("="):
            break
        if keeping:
            lines.append(line)
    return lines


def whole_suite() -> int:
    count, began = shard_count(), time.monotonic()
    with tempfile.TemporaryDirectory() as folder:
        shards = [started(index, count, Path(folder)) for index in range(count)]
        print(f"running the suite in {count} shards side by side", flush=True)
        totals: dict[str, int] = {}
        failures: list[str] = []
        for done, (process, output) in enumerate(shards, start=1):
            try:
                process.wait(timeout=SHARD_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                process.kill()
                failures.append(f"shard {done - 1} ran past {SHARD_TIMEOUT_SECONDS} seconds and was stopped")
            text = output.read_text()
            for name, number in outcome(text).items():
                totals[name] = totals.get(name, 0) + number
            failures.extend(failure_lines(text))
            took = next((line.rsplit(" in ", 1)[-1] for line in reversed(text.splitlines()) if COUNTS.search(line) and " in " in line), "")
            print(f"shards finished {done}/{count} [{round(100 * done / count):3d}%], shard {done - 1} in {took}", flush=True)
        for line in failures:
            print(line)
        summary = ", ".join(f"{totals[name]} {name}" for name in ("failed", "errors", "passed", "skipped") if totals.get(name))
        print(f"{summary or 'no tests ran'} in {time.monotonic() - began:.2f}s")
        return 1 if totals.get("failed") or totals.get("errors") or not totals.get("passed") or any(process.returncode not in (0, 5) for process, _ in shards) else 0


def main(arguments: list[str]) -> int:
    if arguments:
        return subprocess.run([*PYTEST, *arguments], cwd=ROOT).returncode
    return whole_suite()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
