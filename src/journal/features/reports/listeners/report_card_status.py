from journal.chat.process_cards import ProcessCards
from journal.chat.row_process_card import RowProcessCard
from journal.events.listener import Listener
from journal.events.models.updated import Updated
from journal.models.report import Report
from journal.support.agent_actor import AgentActor
from journal.support.subagent_actor import SubagentActor

class ReportCardStatus(Listener[Updated]):
    """A report's card in the chat changes in place from being written to ready, and back, when its status changes."""

    actors = (AgentActor, SubagentActor)

    def __init__(self, card: RowProcessCard, cards: ProcessCards) -> None:
        self.card, self.cards = card, cards

    def handle(self, event: Updated) -> None:
        report = event.model
        if not isinstance(report, Report) or "unfinished" not in event.changed():
            return
        contents = self.card.card_contents(report.environment_id, report, event.actor)
        if self.cards.is_shown(contents):
            self.cards.show(contents)
