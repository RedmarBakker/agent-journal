from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImportTally:
    """What one kind migrated: how many rows, and each row not migrated with the reason."""

    row_type: str
    count: int = 0
    skipped: tuple[str, ...] = field(default_factory=tuple)

    def line(self) -> str:
        return f"| {self.row_type} | {self.count} | {len(self.skipped)} |"
