from dataclasses import dataclass


@dataclass(frozen=True)
class ReaderDraft:
    """A reader the journal drafts for a run that ended, by the run's output number, the part of its line a reader would read, the reader add command filled from the run's own output, and whether the part was suggested before with its runs since; it is due when never suggested, or once the runs since reach the repeat the user set."""

    output: int
    part: str
    command: str
    suggested: bool = False
    later_runs: int = 0

    def is_suggestible(self, repeat_runs: int) -> bool:
        return not self.suggested or 0 < repeat_runs <= self.later_runs
