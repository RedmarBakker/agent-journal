from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class RuleCreated(RowEvent):
    """A rule was written, by the agent or by the user."""

    feature_name = "memory"

    agent_origin: bool
