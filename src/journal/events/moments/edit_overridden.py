from dataclasses import dataclass

from journal.events.moments.sync_moment import SyncMoment
from journal.models.support.ref import Ref


@dataclass(frozen=True, kw_only=True)
class EditOverridden(SyncMoment):
    """The team server kept a colleague's edit of a field over this machine's."""

    writer: str
    noun: str
    row_id: int
    field: str
    field_value: str
    ref: Ref
