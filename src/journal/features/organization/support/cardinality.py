from enum import StrEnum


class Cardinality(StrEnum):
    """How many instances of a Role run: one for all plans, one for each plan, or one for each job in parallel."""

    JOURNAL = "journal"
    PLAN = "plan"
    MANY = "many"

    def is_queued(self) -> bool:
        return self is Cardinality.JOURNAL
