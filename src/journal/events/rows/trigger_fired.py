from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.models.trigger_action import TriggerAction


@dataclass(frozen=True, kw_only=True)
class TriggerFired(RowEvent):
    """A trigger set for a time reached it: its line goes to the agent as its action says, waking an idle session as any line does."""

    feature_name = "triggers"

    text: str
    action: TriggerAction
