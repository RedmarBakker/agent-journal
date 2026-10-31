from journal.chat.moment_cards import MomentCards
from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.supervisor_link import SupervisorLink
from journal.support.card_outcome import CardOutcome
from journal.support.card_type import CardType

LOSS_LABEL = "The supervisor stopped, so your messages reach the agent only at its next step"
LOSS_DETAIL = "End this session and start it again with journal in a terminal."


class SupervisorLossNotice(AgentListener[Ticked]):
    """A supervisor whose inbox is still announced but no longer answers was stopped without closing it: the main agent's chat gets one red card for each loss."""

    def __init__(self, supervisor: SupervisorLink, cards: MomentCards) -> None:
        self.supervisor, self.cards = supervisor, cards
        self.lost_environments: set[int] = set()

    def handle(self, event: Ticked) -> None:
        if not event.agent.is_main():
            return
        if not self.supervisor.is_lost(event.environment_id):
            self.lost_environments.discard(event.environment_id)
            return
        if event.environment_id in self.lost_environments:
            return
        self.lost_environments.add(event.environment_id)
        self.cards.show(event.environment_id, event.session, LOSS_LABEL, detail=LOSS_DETAIL, shows=CardType.FAULTS, outcome=CardOutcome.WARNED)
