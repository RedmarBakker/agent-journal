from dataclasses import dataclass

from journal.features.memory.support.row_count import FORM, RowCount
from journal.repositories.row_counts import RowCounts
from journal.support.rejection import Rejection

JOINTS = ("all", "any")


@dataclass(frozen=True)
class RowCondition:
    """A memory row's condition: its counts, all or any of which must hold; one with no counts always holds."""

    joint: str
    counts: tuple[RowCount, ...]

    @classmethod
    def read(cls, payload: dict) -> "RowCondition":
        if not payload:
            return cls("all", ())
        joint = next((name for name in JOINTS if name in payload), "")
        if not joint:
            return cls("all", (RowCount.read(payload),))
        parts = payload[joint]
        if not isinstance(parts, list) or not parts:
            raise Rejection(FORM)
        return cls(joint, tuple(RowCount.read(part) for part in parts))

    def is_true(self, counts: RowCounts) -> bool:
        results = (count.is_true(counts) for count in self.counts)
        return all(results) if self.joint == "all" else any(results)
