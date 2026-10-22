from dataclasses import dataclass


@dataclass(frozen=True)
class PreviewRow:
    """One thing a plugin runs, listens for, blocks, needs or adds, as its preview lists it: a kind, a label and the command or names."""

    kind: str
    label: str
    command: str = ""
