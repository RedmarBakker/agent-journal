from journal.features.faults.support.nudge_counts import NudgeCounts
from journal.http.support.request import Request
from journal.support.response import Response


class NudgeCountController:
    """The nudges each agent was sent, counted, for the Developer tab, and the reset that sets the counts back to zero."""

    def __init__(self, counts: NudgeCounts) -> None:
        self.counts = counts

    def index(self, request: Request) -> Response:
        return Response.json({"agents": self.counts.rows()})

    def reset(self, request: Request) -> Response:
        self.counts.reset()
        return self.index(request)
