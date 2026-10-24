from journal.chat.process_card import ProcessCard
from journal.chat.process_mark import ProcessMark
from journal.events.moments.plugin_card_asked import PluginCardAsked
from journal.models.message import Message
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class PluginProcessCard(ProcessCard):
    """The process card of a plugin's card that carries a key: a later card of the same key replaces it where it stands if the user has not written since, else at the bottom of the chat."""

    name = "plugin"

    def mark(self, asked: PluginCardAsked) -> ProcessMark:
        return ProcessMark(self.name, asked.environment_id, asked.card_key, asked.label, asked.data, Actor.plugin(asked.plugin), CardKind.PLUGINS, False, asked.detail)

    def refresh(self, message: Message) -> dict:
        return {"active": False}
