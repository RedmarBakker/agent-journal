from dataclasses import dataclass


@dataclass(frozen=True)
class TitledRun:
    """A running output by its number and the title its card shows."""

    id: int
    title: str

    def has_flag_or_path(self) -> bool:
        return any(len(word) > 1 and word[0] == "-" or word.startswith(("/", "~/", "./", "../")) for word in self.title.split())
