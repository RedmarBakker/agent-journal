from dataclasses import dataclass, field

from sync_server.logged_change import LoggedChange


@dataclass(frozen=True)
class PushedChange:
    """One change as a device sends it: the row's table and number, whether it was created, updated, deleted or withdrawn from the team, who wrote it, the fields it set and when each was changed by the device's clock, the device's own number for it, by which a push sent again is known, and for a withdrawn row who keeps it."""

    row_table: str
    row: int
    action: str
    actor: str
    fields: dict = field(default_factory=dict)
    changed_at: dict = field(default_factory=dict)
    local_number: int = 0
    kept_by: str = ""

    def logged_change(self, account_id: int, device_id: int, clock_offset: float) -> LoggedChange:
        return LoggedChange(self.row_table, self.row, self.action, self.actor, account_id, device_id, dict(self.fields), {name: seconds + clock_offset for name, seconds in self.changed_at.items()}, kept_by=self.kept_by)
