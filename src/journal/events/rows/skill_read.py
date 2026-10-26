from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class SkillRead(RowEvent):
    """The agent read one of the journal's skills: the pending read of that skill is done."""

    feature_name = "skills"

    skill: str
