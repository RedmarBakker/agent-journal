from dataclasses import dataclass

from journal.events.models.synced import Synced
from journal.models.model import Model


@dataclass(frozen=True, kw_only=True)
class SyncedUpdate(Synced):
    """A change another machine made to a row reached this one; previous is the row as it stood here before it."""

    previous: Model
