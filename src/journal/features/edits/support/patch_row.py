from dataclasses import dataclass


@dataclass(frozen=True)
class PatchRow:
    """One line of an edit: added, removed or around them, its number in the file, and its text."""

    line_type: str
    line: int
    text: str
    hidden: int = 0
