import os
from pathlib import Path

from journal.features.shell.support.readers import Readers
from journal.features.workers.support.whole_suite import TEST_COMMANDS
from journal.support.chain import Chain
from journal.support.command_classifier import CommandClassifier

# the label a reader of test runs carries
TEST_LABEL = "Running tests"
# the quotes a cd's folder may stand in, as CommandOutputs.ran_within reads them
QUOTES = "\"'"


class TestRunFolder:
    """The folder a shell line runs its tests in: the hook's working folder, changed by each cd before the test, where a test is a command a reader of test runs reads, or one of the test commands the journal knows; a group in brackets is read inside, and a cd's folder may be quoted. A line runs the whole suite when a test command the journal knows is given only options."""

    __test__ = False

    def __init__(self, readers: Readers, classifier: CommandClassifier) -> None:
        self.readers, self.classifier = readers, classifier

    def folder(self, line: str, working: str) -> str:
        folder = Path(working)
        for part in self.parts(line):
            words = part.split()
            if words[:1] == ["cd"] and len(words) > 1:
                folder = folder / os.path.expanduser(part[2:].strip().strip(QUOTES))
            elif self.is_test(part):
                return str(folder.resolve())
        return ""

    def parts(self, line: str) -> list[str]:
        texts = [part.text.strip() for part in Chain.parts(line)]
        return [inner for text in texts for inner in (self.parts(text[1:-1]) if text.startswith("(") and text.endswith(")") else [text])]

    def is_test(self, part: str) -> bool:
        return self.is_known_test(part) or any(reader.commands.reads(part) for reader in self.readers.all() if reader.label == TEST_LABEL)

    def is_whole_run(self, line: str) -> bool:
        return any(all(word.startswith("-") for word in arguments) for part in self.parts(line) for arguments in self.known_arguments(part))

    def is_known_test(self, part: str) -> bool:
        return bool(self.known_arguments(part))

    def known_arguments(self, part: str) -> list[list[str]]:
        runner = part.split(" ", 1)
        texts = (part, *runner[1:2]) if self.classifier.runs_script_file(runner[0]) else (part,)
        return [text.removeprefix(command).split() for text in texts for command in TEST_COMMANDS if text == command or text.startswith(f"{command} ")]
