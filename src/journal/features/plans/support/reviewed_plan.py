from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewedPlan:
    """A plan whose reviewers are all back, with the reports filed about it during its review that are still unread, by number."""

    plan: int
    reports: tuple[int, ...] = ()
