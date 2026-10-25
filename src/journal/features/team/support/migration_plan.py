from collections import Counter
from dataclasses import dataclass, field

from journal.models.outgoing_change import KEPT_BY_ALL, OutgoingChange


@dataclass(frozen=True)
class MigrationPlan:
    """What journal team migrate does: the hub environment it makes, the rows it moves into it by table and number, every row it withdraws from the team server with who keeps it, by each keeper's stamp and name, and the environments that stay on the team."""

    team_key: str
    hub: str
    moved: tuple[tuple[str, int], ...]
    withdrawals: tuple[OutgoingChange, ...]
    kept: tuple[str, ...]
    keepers: dict[str, str] = field(default_factory=dict)

    def lines(self) -> list[str]:
        return [f"makes the hub environment {self.hub}", *(self.withdrawn_line(kept_by) for kept_by in sorted({change.kept_by for change in self.withdrawals})), self.moved_line(), f"keeps on the team, with everything in them: {', '.join(self.kept) or 'no environment'}"]

    def moved_line(self) -> str:
        counts = Counter(table for table, _ in self.moved)
        return "moves into the hub, free to edit: " + (", ".join(f"{count} of {table}" for table, count in sorted(counts.items())) or "nothing")

    def withdrawn_line(self, kept_by: str) -> str:
        counts = Counter(change.row_table for change in self.withdrawals if change.kept_by == kept_by)
        keeper = "every journal keeping its copy" if kept_by == KEPT_BY_ALL else f"kept by {self.keepers[kept_by]} alone"
        return f"withdraws from the team server, {keeper}: " + ", ".join(f"{count} of {table}" for table, count in sorted(counts.items()))
