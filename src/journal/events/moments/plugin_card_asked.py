from dataclasses import dataclass

from journal.events.moments.plugin_moment import PluginMoment


@dataclass(frozen=True, kw_only=True)
class PluginCardAsked(PluginMoment):
    """A plugin's answer asked for a card in the chat: its label and data, its detail, and its key when a later card of the key is to replace it."""

    label: str
    data: dict
    detail: str
    card_key: str
