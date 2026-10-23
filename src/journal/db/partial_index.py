from dataclasses import dataclass, field

from journal.db.index import Index


@dataclass(frozen=True)
class PartialIndex(Index):
    """An index that keeps only the rows its condition picks."""

    condition: str = field(kw_only=True)

    def sql(self) -> str:
        return f"{super().sql()} WHERE {self.condition}"
