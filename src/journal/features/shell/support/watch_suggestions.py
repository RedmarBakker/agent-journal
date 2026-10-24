from journal.engine.nudge import Nudge
from journal.features.shell.support.readers import Readers
from journal.features.shell.shell_nudges import ShellNudges


class WatchSuggestions:
    """What a command moved to the background is informed it may do: watch it as it runs so the user sees it progress, through the reader whose commands it runs; one no reader reads is the shell's reader demand."""

    def __init__(self, readers: Readers) -> None:
        self.readers = readers

    def lines(self, number: int, part: str) -> list[Nudge]:
        reader = self.readers.reading(part)
        return [ShellNudges.WATCH_SUGGESTION.create(n=number, reader=f" --reader {reader.name}" if reader is not None else "")]
