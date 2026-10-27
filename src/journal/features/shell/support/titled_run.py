from dataclasses import dataclass


@dataclass(frozen=True)
class TitledRun:
    """A run of the agent's by its number, the title its card shows, the line the card shows and the topic its reader picks from that line."""

    id: int
    title: str
    line: str
    topic: str

    def is_flagged(self) -> bool:
        return any(len(word) > 1 and word[0] == "-" or word.startswith(("/", "~/", "./", "../")) for word in self.title.split())

    def clashes(self, other: "TitledRun") -> bool:
        return self.title == other.title and self.line != other.line and not self.topic and not other.topic
