import shlex
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestSelection:
    """The arguments a worker names its tests with, as the project's test command takes them: whether they name any test, an option or a folder alone running the whole suite, and the arguments another list has that they lack."""

    words: tuple[str, ...]

    @classmethod
    def parsed(cls, arguments: str) -> "TestSelection":
        return cls(tuple(shlex.split(arguments)))

    @classmethod
    def printed(cls, text: str) -> "TestSelection":
        return cls(tuple(line.strip() for line in text.splitlines() if line.strip()))

    def names_tests(self, folder: Path) -> bool:
        return any(not word.startswith("-") and not (folder / word).is_dir() for word in self.words)

    def missing(self, selection: "TestSelection") -> tuple[str, ...]:
        return tuple(word for word in selection.words if word not in self.words)
