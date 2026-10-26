from journal.config import Config
from journal.features.seed import Seed
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.shell.support.readers import Readers

SHIPPED = (
    Reader("pytest", "the failed tests of a pytest run with their assertion lines, its summary, or the error that stopped it", r"^FAILED |^ERROR |^E +(assert\b|\w*(Error|Exception)\b)|^(=+ )?([0-9]+ (passed|failed|errors?|deselected)\b|no tests ran)|^ERROR: .{1,70}$", r"\[ *([0-9]+)%\]", "Running tests", ReaderCommands(("pytest",)), r"[.FEsxX]", r"(\S+\.py)\b|-k\s+(\"[^\"]+\"|'[^']+'|\S+)",
           r"^(=+ )?[0-9]+ passed", r"^(=+ )?([0-9]+ (failed|errors?|deselected)\b|no tests ran)|^ERROR: .{1,70}$", summary_pattern=r"(?:([0-9]+ failed), )?([0-9]+ passed)"),
    Reader("vitest", "the failed tests of a vitest run with their assertion lines, and its totals", r"^\s*FAIL |^\s*(Assertion|Type|Reference)?Error\b|^\s*(Test Files|Tests)\s+[0-9]", "", "Running tests", ReaderCommands(("vitest",)),
           finished_pattern=r"^\s*(Test Files|Tests)\s+[0-9]", failed_pattern=r"^\s*FAIL |^\s*Tests\s+[0-9]+ failed", summary_pattern=r"^\s*Tests\s+(?:([0-9]+ failed)\s*\|\s*)?([0-9]+ passed)"),
    Reader("dotnet-test", "the failed tests and the totals of a dotnet test run", r"Failed |error |Passed!|Failed!|Total tests", "", "Running tests", ReaderCommands(("dotnet test",)), finished_pattern=r"Passed!|Total tests", failed_pattern=r"Failed |Failed!|error "),
    Reader("phpunit", "the failures and the totals of a phpunit or pest run", r"FAILURES!|ERRORS!|Tests: |FAIL |Failed asserting|OK \(", r"\( *([0-9]+)%\)", "Running tests", ReaderCommands(("phpunit", "pest", "artisan test")), r"[.FEWRSI]",
           finished_pattern=r"OK \(|Tests: ", failed_pattern=r"FAILURES!|ERRORS!|FAIL |Failed asserting|Tests: "),
    Reader("worker-merge", "a worker merge: the task it closed and the commit, the next task the worker went on to, or why it was not merged: a plugin's hold with its sins, a clash or a refusal", r"^step [0-9]+/[0-9]+: |^now: .{1,120}$|^task [0-9]+ done: [^;]{1,90}$|^it went |^worker [0-9]+'s work was not merged: [^;,]{1,60}$|^worker [0-9]+ is [^;]{1,80}$|carries [0-9]+ sins?:?$", r"^step ([0-9]+)/([0-9]+): ", "Merging the checked workers' work", ReaderCommands(("journal worker merge",)),
           topic_pattern=r"journal worker merge +([0-9]+)", topic_label="Merging worker {topic}'s work",
           finished_pattern=r"^task [0-9]+ done: [^;]{1,90}$", failed_pattern=r"^worker [0-9]+'s work was not merged: [^;,]{1,60}$|^worker [0-9]+ is [^;]{1,80}$|carries [0-9]+ sins?:?$"),
)


RETIRED_LABELS = ("Tests", "Running the tests", "Merging a worker's work")
RETIRED_READERS = ("git-commit", "git-push")
RETIRED_PATTERNS = (r"^step [0-9]+/[0-9]+: |^task [0-9]+ done: [^;]{1,90}$|^it went |^worker [0-9]+'s work was not merged: [^;,]{1,60}$|^worker [0-9]+ is [^;]{1,80}$|carries [0-9]+ sins?:?$", r"^(=+ )?([0-9]+ (passed|failed|errors?|deselected)\b|no tests ran)|^ERROR: .{1,70}$",)


class DefaultReaders(Seed):
    """The readers the journal ships, for pytest, vitest, dotnet test, phpunit or pest and a worker merge, written into the project's readers at boot when a reader of that name is not there yet, or is still one shipped earlier, with an older label or a missing part, as working examples a test run is informed about."""

    def __init__(self, config: Config, readers: Readers) -> None:
        self.config, self.readers = config, readers

    def run(self) -> None:
        for name in RETIRED_READERS:
            if self.readers.found(name) is not None:
                self.readers.removed(name)
        for reader in SHIPPED:
            if not any((self.config.readers / f"{reader.name}{suffix}").is_file() for suffix in (".pattern", ".sh")) or self.is_retired(reader):
                self.readers.stock(reader)

    def is_retired(self, shipped: Reader) -> bool:
        path = self.config.readers / f"{shipped.name}.pattern"
        if not path.is_file():
            return False
        existing = self.readers.lookup(shipped.name)
        return existing.label in RETIRED_LABELS or existing.pattern in RETIRED_PATTERNS or (existing.label == shipped.label and self.has_missing_pattern(existing, shipped))

    @staticmethod
    def has_missing_pattern(existing: Reader, default: Reader) -> bool:
        return (not existing.topic_pattern and bool(default.topic_pattern)) or (not existing.finished_pattern and bool(default.finished_pattern)) or (not existing.summary_pattern and bool(default.summary_pattern))
