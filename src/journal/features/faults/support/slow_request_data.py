from typing import TypedDict


class SlowRequestData(TypedDict):
    """The slow request tally as the chat mark keeps it in its data."""

    routes: dict[str, list[int]]
    gathered: int
    costliest_route: str
    worst_points: int
    flagged_at: float
    reported_at: float
