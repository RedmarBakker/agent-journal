from dataclasses import dataclass


@dataclass(frozen=True)
class MessageRequirement:
    """The messages a demand of the messages feature asks the agent to read or answer, and the folders of their files, which it may read meanwhile."""

    numbers: tuple[int, ...]
    folders: tuple[str, ...] = ()

    def listing(self) -> str:
        return ", ".join(str(n) for n in self.numbers)
