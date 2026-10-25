import os
from pathlib import Path

from journal.features.shell.support.readers import Readers
from journal.features.workers.support.tool_use_counts import TEST_COMMANDS
from journal.support.chain import Chain

# the label a reader of test runs carries
TEST_LABEL = "Running tests"
# the interpreters a test script is run with, such as python3 scripts/suite.py
INTERPRETERS = ("python3 ", "python ")


class TestRunFolder:
    """The folder a shell line runs its tests in: the hook's working folder, changed by each cd before the test, where a test is a command a reader of test runs reads, or one of the test commands the journal knows; a group in brackets is read inside."""

    __test__ = False

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def folder(self, line: str, working: str) -> str:
        folder = Path(working)
        for part in self.parts(line):
            words = part.split()
            if words[:1] == ["cd"] and len(words) > 1:
                folder = folder / os.path.expanduser(words[1])
            elif self.is_test(part):
                return str(folder.resolve())
        return ""

    def parts(self, line: str) -> list[str]:
        texts = [part.text.strip() for part in Chain.parts(line)]
        return [inner for text in texts for inner in (self.parts(text[1:-1]) if text.startswith("(") and text.endswith(")") else [text])]

    def is_test(self, part: str) -> bool:
        return self.is_known_test(part) or any(reader.commands.reads(part) for reader in self.readers.all() if reader.label == TEST_LABEL)

    @staticmethod
    def is_known_test(part: str) -> bool:
        texts = (part, *(part.removeprefix(interpreter) for interpreter in INTERPRETERS if part.startswith(interpreter)))
        return any(text == command or text.startswith(f"{command} ") for text in texts for command in TEST_COMMANDS)
