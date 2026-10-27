"""Runs the test suite: a run naming tests or options is one pytest run that counts its finished tests against its total as it goes; the whole suite is split into shards run side by side, one per core but two, and their outcomes added up, while the test commandments judge tests/ beside them and fail the run on a sin; --update-matrix runs the update matrix in five shards instead, unless JOURNAL_SKIP_UPDATE_MATRIX is set; --coverage-map runs the whole suite noting which source files each test runs, for scripts/affected_tests.py; a run of the simulator's files runs at a lower priority."""
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
# what one shard holds in memory, measured at about 210 MB a shard process and 150 MB a booted module journal, with room to spare
SHARD_BYTES = 300 * 2**20
# the pages macOS can hand a new process without swapping
RECLAIMABLE_PAGES = ("free", "inactive", "speculative")
SHARD_TIMEOUT_SECONDS = 600
COUNTS = re.compile(r"(\d+) (passed|failed|errors?|skipped|deselected|xfailed|xpassed)")
# the progress line the commandments judge writes at each of its stages
JUDGE_PROGRESS = re.compile(r"^(parsing|reading|detector) (\d+)/(\d+)$")
FAILURE_START = re.compile(r"^(=+ (FAILURES|ERRORS) =+|_{3,} .+ _{3,})$")
SUMMARY_START = re.compile(r"^=+ short test summary info =+$")
PERCENT = re.compile(r"\[\s*(\d+)%\]")
COLLECTED = re.compile(r"collected (\d+) items?(?: / (\d+) deselected)?")
RESULT_LINE = re.compile(r"^(?:tests/\S+ )?([.FEsxX]+)(?=\s*\[\s*\d+%\]|\s*$|\S)")
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
MATRIX_OPTION = "--update-matrix"
COVERAGE_OPTION = "--coverage-map"
# which source files each test runs, read by scripts/affected_tests.py
COVERAGE_MAP_FILE = ROOT / ".journal" / "runtime" / "test-coverage.json"
COVERAGE_OUT_VARIABLE = "JOURNAL_COVERAGE_OUT"
MATRIX_FILE = "tests/update_matrix_run.py"
MATRIX_SHARDS = 5
MATRIX_SKIP_VARIABLE = "JOURNAL_SKIP_UPDATE_MATRIX"


def shard_count(available: int) -> int:
    return max(1, min(core_shards(), available // SHARD_BYTES))


def core_shards() -> int:
    return max(1, min(MOST_SHARDS, (os.cpu_count() or 2) - SPARE_CORES))


def available_bytes() -> int:
    meminfo = Path("/proc/meminfo")
    return meminfo_available(meminfo.read_text()) if meminfo.is_file() else vm_stat_available(subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout)


def meminfo_available(text: str) -> int:
    return int(re.search(r"^MemAvailable:\s+(\d+) kB", text, re.M).group(1)) * 1024


def vm_stat_available(text: str) -> int:
    page = int(re.search(r"page size of (\d+) bytes", text).group(1))
    return page * sum(int(re.search(rf"^Pages {kind}:\s+(\d+)\.", text, re.M).group(1)) for kind in RECLAIMABLE_PAGES)


def memory_line(count: int, available: int) -> str:
    return f"the suite takes {count} shards, not {core_shards()}: only {available // 2**20} MB of memory is free, and a shard takes about {SHARD_BYTES // 2**20} MB"


def started(index: int, count: int, folder: Path, arguments: tuple[str, ...] = ()) -> tuple[subprocess.Popen, Path]:
    output = folder / f"shard-{index}.txt"
    environ = {**os.environ, SHARD_VARIABLE: f"{index}/{count}", "PYTHONUNBUFFERED": "1", DURATIONS_IN_VARIABLE: str(DURATIONS_FILE), DURATIONS_OUT_VARIABLE: str(folder / f"shard-{index}.seconds.json")}
    process = subprocess.Popen([*PYTEST, *arguments], cwd=ROOT, env=environ, stdout=output.open("w"), stderr=subprocess.STDOUT)
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
            print(ending_line(shards) if finished >= total and percent == shown else progress_line(finished, total), flush=True)
            shown, last_shown = percent, time.monotonic()
        time.sleep(PROGRESS_SECONDS)


# every test has finished and the run waits for shards still ending, named so a card at 100% says what it waits on
def ending_line(shards: list[tuple[subprocess.Popen, Path]]) -> str:
    running = [str(index) for index, (process, _) in enumerate(shards) if process.poll() is None]
    return f"every test finished; waiting for shard {', '.join(running)} to end"


def progress_line(finished: int, total: int) -> str:
    return f"running tests [{100 * finished // total if total else 0:3d}%] {finished} of {total} finished"


def durations_kept(folder: Path) -> None:
    seconds = json.loads(DURATIONS_FILE.read_text()) if DURATIONS_FILE.is_file() else {}
    for path in folder.glob("shard-*.seconds.json"):
        seconds.update(json.loads(path.read_text()))
    DURATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DURATIONS_FILE.write_text(json.dumps(seconds))


def whole_suite() -> int:
    with tempfile.TemporaryDirectory() as folder:
        judging = commandments_started(Path(folder))
        available = available_bytes()
        count = shard_count(available)
        if count < core_shards():
            print(memory_line(count, available), flush=True)
        failed = sharded_run(Path(folder), count, (), "the suite")
        print("waiting for the test commandments judging tests/", flush=True)
        sinful = commandments_judged(judging)
        return 1 if sinful or failed else 0


# every pair of releases is a test of its own, so the update matrix splits over a few processes however many cores there are
def update_matrix() -> int:
    if os.environ.get(MATRIX_SKIP_VARIABLE):
        print(f"the update matrix is skipped: {MATRIX_SKIP_VARIABLE} is set", flush=True)
        return 0
    with tempfile.TemporaryDirectory() as folder:
        return 1 if sharded_run(Path(folder), MATRIX_SHARDS, (MATRIX_FILE,), "the update matrix") else 0


def sharded_run(folder: Path, count: int, arguments: tuple[str, ...], name: str) -> bool:
    began = time.monotonic()
    shards = [started(index, count, folder, arguments) for index in range(count)]
    print(f"running {name} in {count} shards side by side", flush=True)
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
        for key, number in outcome(text).items():
            totals[key] = totals.get(key, 0) + number
        failures.extend(failure_lines(text))
        took = next((line.rsplit(" in ", 1)[-1] for line in reversed(text.splitlines()) if COUNTS.search(line) and " in " in line), "")
        print(f"shards finished {done}/{count} [{round(100 * done / count):3d}%], shard {done - 1} in {took}", flush=True)
    durations_kept(folder)
    for line in failures:
        print(line)
    summary = ", ".join(f"{totals[key]} {key}" for key in ("failed", "errors", "passed", "skipped") if totals.get(key))
    print(f"{summary or 'no tests ran'} in {time.monotonic() - began:.2f}s")
    return bool(totals.get("failed") or totals.get("errors") or any(process.returncode not in (0, 5) for process, _ in shards))


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
    if not judge_waited(process, output):
        process.kill()
        print(f"the test commandments ran past {SHARD_TIMEOUT_SECONDS} seconds and were stopped")
        return True
    if process.returncode == 0:
        print("the tests break none of the test commandments")
        return False
    print("the tests break the test commandments (tests-drive-the-real-path):")
    print(output.read_text(), end="", flush=True)
    return True


def judge_waited(process: subprocess.Popen, output: Path) -> bool:
    deadline, shown = time.monotonic() + SHARD_TIMEOUT_SECONDS, ""
    while process.poll() is None:
        if time.monotonic() > deadline:
            return False
        line = judge_progress(output.read_text(errors="replace"))
        if line and line != shown:
            print(line, flush=True)
            shown = line
        time.sleep(1)
    return True


def judge_progress(text: str) -> str:
    steps = [match for line in re.split(r"[\r\n]", text) if (match := JUDGE_PROGRESS.match(line.strip()))]
    if not steps:
        return ""
    stage, done, total = steps[-1].groups()
    return f"judging tests/: {stage} {done}/{total} [{round(100 * int(done) / max(int(total), 1)):3d}%]"


def coverage_map() -> int:
    with tempfile.TemporaryDirectory() as folder:
        os.environ[COVERAGE_OUT_VARIABLE] = folder
        failed = sharded_run(Path(folder), shard_count(available_bytes()), (), "the suite, noting which source files each test runs")
        covered = {node: files for path in Path(folder).glob("shard-*.coverage.json") for node, files in json.loads(path.read_text()).items()}
        COVERAGE_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
        COVERAGE_MAP_FILE.write_text(json.dumps(covered))
        print(f"the source files of {len(covered)} tests are written to {COVERAGE_MAP_FILE}", flush=True)
        return 1 if failed else 0


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
    if arguments == [MATRIX_OPTION]:
        return update_matrix()
    if arguments == [COVERAGE_OPTION]:
        return coverage_map()
    if arguments:
        return scoped_run(arguments)
    return whole_suite()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
