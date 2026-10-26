import re

from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.reader import Reader
from journal.models.command_output import FAILED, FINISHED

# lines of unrelated runs: a pattern that picks every one of them picks every line of any run
UNRELATED_LINES = ("a", "Running tests", "#4 [php 2/9] RUN apt-get install -y git", "  ✓ it adds a row 0.04s", "PASS  Tests\\Unit\\OrderTest", "error: not found", "123", "Pokemon Booster 65/131")
# the summary lines of the common test runners: pest and phpunit, pytest, vitest, jest, dotnet test
TEST_SUMMARIES = ("Tests:    41 passed (105 assertions)", "Tests:  2 failed, 39 passed (105 assertions)", "===== 2 failed, 40 passed in 3.21s =====", "Test Files  2 passed (2)", "Tests:       1 failed, 3 passed, 4 total", "Passed!  - Failed:     0, Passed:    12, Skipped:     0, Total:    12")
# the failure lines of the same runners
TEST_FAILURES = ("FAILED  Tests\\Unit\\OrderTest > it ships the order", "  ⨯ it ships the order", "FAILED tests/test_orders.py::test_ships - AssertionError", "FAIL  src/orders.test.ts > ships the order", "  ✕ ships the order (12 ms)", "  Failed OrderTests.Ships [12 ms]")
TESTING = "testing"


class ReaderProbes:
    """What a reader picks of fixed sample lines, so a reader that filters nothing, or a test run's reader that would miss both the summary and the failures of a real run, is refused when it is added, whatever the stored run it was tried on happened to print."""

    @staticmethod
    def unfiltered_patterns(reader: Reader) -> list[str]:
        patterns = {"--pattern": reader.pattern, "--finished": reader.finished_pattern, "--failed": reader.failed_pattern}
        return [flag for flag, pattern in patterns.items() if pattern and all(re.search(pattern, line) for line in UNRELATED_LINES)]

    @staticmethod
    def is_test_reader(reader: Reader) -> bool:
        return any(ActivityLabel.line_label(program) == TESTING for program in reader.commands.programs)

    # a test run's reader selects what a person needs at its end, its summary or its failures; progress is asked of it only once a
    # run prints a count, while it runs, since demanding it of a runner that prints none would bring a progress that lies
    @classmethod
    def test_run_misses(cls, reader: Reader) -> list[str]:
        if reader.script or not cls.is_test_reader(reader):
            return []
        summaries = any(reader.variant(FINISHED).card_lines([line]) or reader.variant(FAILED).card_lines([line]) for line in TEST_SUMMARIES)
        failures = reader.card_lines(list(TEST_FAILURES)) or reader.variant(FAILED).card_lines(list(TEST_FAILURES))
        if summaries or failures:
            return []
        return [f"it reads a test run and selects neither its summary, such as \"{TEST_SUMMARIES[0].strip()}\", nor its failures, such as \"{TEST_FAILURES[0]}\": give it a --finished and a --failed pattern for the summary of the runner and a pattern for its failed tests"]

    @classmethod
    def reads_test_runs(cls, reader: Reader) -> bool:
        return bool(reader.script) or not cls.test_run_misses(reader)
