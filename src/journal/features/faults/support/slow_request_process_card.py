from journal.chat.process_card import ProcessCard
from journal.chat.process_mark import ProcessMark
from journal.events.moments.slow_requests_reported import SlowRequestsReported
from journal.models.message import Message
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class SlowRequestProcessCard(ProcessCard):
    """The process card of the slow requests: how many went over their budget, and the slowest routes with their worst time and count, a new mark in the chat each time the agent is told of them."""

    KEY = "slow:requests"
    name = "slow_request"

    def mark(self, reported: SlowRequestsReported) -> ProcessMark:
        return ProcessMark(self.name, reported.environment_id, f"{self.KEY}:{int(reported.moment)}", f"Slow requests report ready: {reported.total} over budget, read it with journal developer slowest", reported.data, Actor.system(), CardKind.FAULTS, False, reported.detail)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
