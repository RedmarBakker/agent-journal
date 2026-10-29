from dataclasses import dataclass


@dataclass(frozen=True)
class LibraryEntry:
    """What the library publishes for one sequence, template or profile: its name in the library, its title and the text of its body."""

    name: str
    title: str
    body: str
