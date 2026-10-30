from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal


SetupStatus = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class SetupDiagnostic:
    name: str
    status: SetupStatus
    checked_at: datetime | None
    reason: str
    source_references: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.reason.strip():
            raise ValueError("a setup diagnostic needs a name and reason")
        if self.status not in {"pass", "fail", "unknown"}:
            raise ValueError(f"unknown setup status: {self.status}")
        if self.status != "unknown" and self.checked_at is None:
            raise ValueError("a known setup result needs its check time")
        if self.checked_at is not None and self.checked_at.utcoffset() != timedelta(0):
            raise ValueError("setup evidence times must be UTC")
        if any(not reference.strip() for reference in self.source_references):
            raise ValueError("setup evidence references cannot be empty")
        if len(set(self.source_references)) != len(self.source_references):
            raise ValueError("setup evidence references must be unique")
