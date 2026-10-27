from dataclasses import dataclass, field

from sync_server.row_fields import RowFields


@dataclass(frozen=True)
class StoredRow(RowFields):
    """A row as the server holds it now: each field's value, when it was changed, and the account that changed it."""

    fields: dict = field(default_factory=dict)
    changed_at: dict = field(default_factory=dict)
    writers: dict = field(default_factory=dict)
