from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.plugin_proposed import PluginProposed
from journal.support.card_kind import CardKind


class PluginProposalCard(Listener[PluginProposed]):
    """A plugin the agent proposes is a mark in the chat with the command that installs it."""

    def __init__(self, cards: MomentCards) -> None:
        self.cards = cards

    def handle(self, event: PluginProposed) -> None:
        label = f"The agent proposes the plugin {event.plugin}" + (f": {event.explanation}" if event.explanation else "")
        self.cards.show(event.environment_id, "", label, detail=event.detail, command=event.command, actor=event.actor, shows=CardKind.PLUGINS)
