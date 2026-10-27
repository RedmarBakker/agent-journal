"""Runs the test suite: a run naming tests or options is one pytest run that counts its finished tests against its total as it goes; the whole suite is split into shards run side by side, one per core but two, and their outcomes added up, while the test commandments judge tests/ beside them and fail the run on a sin; a run of the simulator's files runs at a lower priority."""
import json
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
TALLY_VARIABLE = "JOURNAL_TEST_TALLY"
SPARE_CORES = 2
MOST_SHARDS = 8
SHARD_TIMEOUT_SECONDS = 600
COUNTS = re.compile(r"(\d+) (passed|failed|errors?|skipped|deselected|xfailed|xpassed)")
FAILURE_START = re.compile(r"^(=+ (FAILURES|ERRORS) =+|_{3,} .+ _{3,})$")
SUMMARY_START = re.compile(r"^=+ short test summary info =+$")
PERCENT = re.compile(r"\[\s*(\d+)%\]")
COLLECTED = re.compile(r"collected (\d+) items?(?: / (\d+) deselected)?")
RESULT_LINE = re.compile(r"^(?:tests/\S+ )?([.FEsxX]+)\s*(?:\[\s*\d+%\])?$")
PROGRESS_SECONDS = 2.0
HEARTBEAT_SECONDS = 10.0
DURATIONS_FILE = ROOT / ".journal" / "runtime" / "suite-durations.json"
DURATIONS_IN_VARIABLE = "JOURNAL_TEST_DURATIONS_IN"
DURATIONS_OUT_VARIABLE = "JOURNAL_TEST_DURATIONS_OUT"
JUDGE = ROOT / ".journal" / "plugins" / "code-commandments" / "bin" / "commandments-release"
LOW_PRIORITY = ["nice", "-n", "10"]
TEST_COMMANDMENTS = [*LOW_PRIORITY, str(JUDGE), "judge", "tests", "--skill=tests-drive-the-real-path", "--no-checklist"]
# a run of the simulator's files keeps the machine busy for minutes, so it runs at a lower priority than the journal beside it
SIMULATION_FILE = "simulation"


def shard_count() -> int:
    return max(1, min(MOST_SHARDS, (os.cpu_count() or 2) - SPARE_CORES))


def started(index: int, count: int, folder: Path) -> tuple[subprocess.Popen, Path]:
    output = folder / f"shard-{index}.txt"
    environ = {**os.environ, SHARD_VARIABLE: f"{index}/{count}", "PYTHONUNBUFFERED": "1", DURATIONS_IN_VARIABLE: str(DURATIONS_FILE), DURATIONS_OUT_VARIABLE: str(folder / f"shard-{index}.seconds.json")}
    process = subprocess.Popen(PYTEST, cwd=ROOT, env=environ, stdout=output.open("w"), stderr=subprocess.STDOUT)
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


def shard_progress(output: Path) -> tuple[int, int]:
    text = output.read_text()
    collected = COLLECTED.search(text)
    total = int(collected[1]) - int(collected[2] or 0) if collected else 0
    done = sum(len(match[1]) for line in text.splitlines() if (match := RESULT_LINE.match(line)))
    return min(done, total), total


def progress_shown(shards: list[tuple[subprocess.Popen, Path]]) -> None:
    shown, began, last_shown = -1, time.monotonic(), 0.0
    while any(process.poll() is None for process, _ in shards) and time.monotonic() - began < SHARD_TIMEOUT_SECONDS:
        counts = [shard_progress(output) for _, output in shards]
        finished, total = sum(done for done, _ in counts), sum(whole for _, whole in counts)
        percent = 100 * finished // total if total else 0
        if total and (percent != shown or time.monotonic() - last_shown >= HEARTBEAT_SECONDS):
            print(progress_line(finished, total), flush=True)
            shown, last_shown = percent, time.monotonic()
        time.sleep(PROGRESS_SECONDS)


def progress_line(finished: int, total: int) -> str:
    return f"running tests [{100 * finished // total if total else 0:3d}%] {finished} of {total} finished"


def durations_kept(folder: Path) -> None:
    seconds = json.loads(DURATIONS_FILE.read_text()) if DURATIONS_FILE.is_file() else {}
    for path in folder.glob("shard-*.seconds.json"):
        seconds.update(json.loads(path.read_text()))
    DURATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DURATIONS_FILE.write_text(json.dumps(seconds))


def whole_suite() -> int:
    count, began = shard_count(), time.monotonic()
    with tempfile.TemporaryDirectory() as folder:
        shards = [started(index, count, Path(folder)) for index in range(count)]
        judging = commandments_started(Path(folder))
        print(f"running the suite in {count} shards side by side", flush=True)
        progress_shown(shards)
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
        durations_kept(Path(folder))
        for line in failures:
            print(line)
        summary = ", ".join(f"{totals[name]} {name}" for name in ("failed", "errors", "passed", "skipped") if totals.get(name))
        print(f"{summary or 'no tests ran'} in {time.monotonic() - began:.2f}s")
        sinful = commandments_judged(judging)
        return 1 if sinful or totals.get("failed") or totals.get("errors") or not totals.get("passed") or any(process.returncode not in (0, 5) for process, _ in shards) else 0


def commandments_started(folder: Path) -> tuple[subprocess.Popen, Path] | None:
    if not JUDGE.is_file():
        print("the test commandments are not judged: the code-commandments plugin is not installed here", flush=True)
        return None
    output = folder / "commandments.txt"
    return subprocess.Popen(TEST_COMMANDMENTS, cwd=ROOT, stdout=output.open("w"), stderr=subprocess.STDOUT), output


def commandments_judged(judging: tuple[subprocess.Popen, Path] | None) -> bool:
    if judging is None:
        return False
    process, output = judging
    try:
        process.wait(timeout=SHARD_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"the test commandments ran past {SHARD_TIMEOUT_SECONDS} seconds and were stopped")
        return True
    if process.returncode == 0:
        print("the tests break none of the test commandments")
        return False
    print("the tests break the test commandments (tests-drive-the-real-path):")
    print(output.read_text(), end="", flush=True)
    return True


def scoped_command(arguments: list[str]) -> list[str]:
    return [*(LOW_PRIORITY if any(SIMULATION_FILE in argument for argument in arguments) else []), *PYTEST, *arguments]


def scoped_run(arguments: list[str]) -> int:
    with tempfile.TemporaryDirectory() as folder:
        output = Path(folder) / "run.txt"
        process = subprocess.Popen(scoped_command(arguments), cwd=ROOT, env={**os.environ, "PYTHONUNBUFFERED": "1", TALLY_VARIABLE: "1"}, stdout=output.open("w"), stderr=subprocess.STDOUT)
        progress_shown([(process, output)])
        try:
            process.wait(timeout=SHARD_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"the run went past {SHARD_TIMEOUT_SECONDS} seconds and was stopped")
        print(progress_line(*shard_progress(output)), flush=True)
        print(output.read_text(), end="", flush=True)
        return process.returncode


def main(arguments: list[str]) -> int:
    if arguments:
        return scoped_run(arguments)
    return whole_suite()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
