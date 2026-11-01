from dataclasses import dataclass

from journal.events.rows.plan_closed import PlanClosed


@dataclass(frozen=True, kw_only=True)
class PlanAbandoned(PlanClosed):
    """A plan was given up, by the user or by a command, with the tasks that were its alone."""

    user_origin: bool
