from dataclasses import dataclass, replace
from typing import Iterable

from journal.support.table_row import TableRow

UNKNOWN = "unknown"
# a chain is named by the kind of its weightiest part: an edit over a read, a test run over a folder change
KIND_ORDER = ("edit", "test run", "build", "package", "network", "version control", "check", "process", "search", "read", "journal", UNKNOWN)
WRITE_EFFECTS = frozenset({"writes_files", "deletes_files"})


@dataclass(frozen=True)
class Classification:
    """What a shell command is and does, read from the command table: its kind, its effects, and whether the line alone leaves its meaning uncertain; a row that names a kind replaces the effects, one that names none adds to them."""

    kind: str = UNKNOWN
    effects: tuple[str, ...] = ()
    uncertain: bool = False

    @classmethod
    def parsed(cls, data: dict) -> "Classification":
        return cls(kind=data.get("kind", UNKNOWN), effects=tuple(data.get("effects", ())), uncertain=bool(data.get("uncertain")))

    @classmethod
    def union(cls, classifications: Iterable["Classification"]) -> "Classification":
        parts = list(classifications)
        if not parts:
            return cls()
        kind = min((part.kind for part in parts), key=lambda kind: KIND_ORDER.index(kind) if kind in KIND_ORDER else len(KIND_ORDER))
        return cls(kind=kind, effects=tuple(sorted({effect for part in parts for effect in part.effects})), uncertain=any(part.uncertain for part in parts))

    def with_row(self, row: TableRow) -> "Classification":
        effects = row.effects if row.kind else (*self.effects, *row.effects)
        return replace(self, kind=row.kind or self.kind, effects=tuple(sorted(set(effects))), uncertain=self.uncertain or row.uncertain)

    def with_effect(self, effect: str) -> "Classification":
        return replace(self, effects=tuple(sorted({*self.effects, effect})))

    @property
    def writes(self) -> bool:
        return bool(WRITE_EFFECTS & set(self.effects)) or self.uncertain and self.kind != UNKNOWN
