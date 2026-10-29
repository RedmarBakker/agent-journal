from dataclasses import dataclass

from journal.models.model import Model
from journal.models.support.ref import Ref

SNIPPET_RADIUS_CHARACTERS = 160


@dataclass(frozen=True)
class SearchHit:
    """One thing a search found: what it is, such as task 12, the passage that holds the words, and the row a click opens, such as tasks:12, empty when it opens none."""

    ref: str
    passage: str
    row: str = ""

    @classmethod
    def build(cls, row: Model, terms: list[str]) -> "SearchHit":
        return cls(f"{row.noun()} {row.id}", cls.excerpt(row.mentioning_text(), terms), str(Ref.build(row)))

    @staticmethod
    def excerpt(text: str, terms: list[str]) -> str:
        flat = " ".join(text.split())
        time = max(0, flat.lower().find(terms[0].lower()) - SNIPPET_RADIUS_CHARACTERS // 4)
        cut = flat[time:time + SNIPPET_RADIUS_CHARACTERS]
        return ("…" if time else "") + cut + ("…" if time + SNIPPET_RADIUS_CHARACTERS < len(flat) else "")

    def line(self) -> str:
        return f"{self.ref}: {self.passage}"

    def card_result(self) -> dict:
        return {"row": self.row, "label": self.ref, "passage": self.passage}
