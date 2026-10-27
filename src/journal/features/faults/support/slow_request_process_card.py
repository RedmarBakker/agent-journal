from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.events.moments.slow_requests_reported import SlowRequestsReported
from journal.models.message import Message
from journal.support.actor import Actor
from journal.support.card_type import CardType


class SlowRequestProcessCard(ProcessCard):
    """The process card of the slow requests: how many went over their budget, and the slowest routes with their worst time and count, a new mark in the chat each time the agent is told of them."""

    KEY = "slow:requests"
    name = "slow_request"

    def card_contents(self, reported: SlowRequestsReported) -> ProcessCardContents:
        return ProcessCardContents(self.name, reported.environment_id, f"{self.KEY}:{int(reported.moment)}", f"{reported.total} slow responses were recorded", reported.data, Actor.system(), CardType.FAULTS, False, reported.detail)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
