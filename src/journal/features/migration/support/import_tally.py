from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImportTally:
    """What one kind migrated: how many rows, and each row not migrated with the reason."""

    kind: str
    count: int = 0
    skipped: tuple[str, ...] = field(default_factory=tuple)

    def line(self) -> str:
        return f"| {self.kind} | {self.count} | {len(self.skipped)} |"
