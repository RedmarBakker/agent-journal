from journal.support.command_shape import CommandShape
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.readers import Readers
from journal.features.shell.shell_nudges import ShellNudges

LONG_RUNS = ("testing", "building")


class WatchSuggestions:
    """What a command moved to the background is informed it may do: watch it as it runs so the user sees it progress, through the reader whose commands it runs; a test run or a build that no reader reads is instructed to make a reader first."""

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def lines(self, number: int, part: str) -> list[str]:
        reader = self.readers.reading(part)
        if reader is not None:
            return [ShellNudges.WATCH_SUGGESTION.create(n=number, reader=f" --reader {reader.name}").rendered()]
        watch = ShellNudges.WATCH_SUGGESTION.create(n=number, reader="").rendered()
        if ActivityLabel.build(part) not in LONG_RUNS:
            return [watch]
        return [watch, ShellNudges.NEW_READER_SUGGESTION.create(command=CommandShape.build(part)).rendered()]
