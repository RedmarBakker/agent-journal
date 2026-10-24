from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.events.moments.plugin_card_requested import PluginCardRequested
from journal.models.message import Message
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class PluginProcessCard(ProcessCard):
    """The process card of a plugin's card that carries a key: a later card of the same key replaces it where it stands if the user has not written since, else at the bottom of the chat."""

    name = "plugin"

    def card_contents(self, question: PluginCardRequested) -> ProcessCardContents:
        return ProcessCardContents(self.name, question.environment_id, question.card_key, question.label, question.data, Actor.plugin(question.plugin), CardKind.PLUGINS, False, question.detail)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
