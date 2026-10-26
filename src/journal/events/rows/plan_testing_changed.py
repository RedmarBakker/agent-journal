from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class PlanTestingChanged(RowEvent):
    """How a plan tests changed: the testing template it follows now, by its title and its instructions, or none."""

    feature_name = "plans"

    plan_id: int
    title: str
    testing: str
