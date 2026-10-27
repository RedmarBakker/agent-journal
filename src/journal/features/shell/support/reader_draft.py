from dataclasses import dataclass


@dataclass(frozen=True)
class ReaderDraft:
    """A reader the journal drafts for a run that ended, by the run's output number, the part of its line a reader would read, and the reader add command filled from the run's own output."""

    output: int
    part: str
    command: str
