from dataclasses import dataclass

# what a plugin's answer names each field of a card, its type as kind
ANSWER_KEYS = {"card_type": "kind", "label": "label", "tone": "tone", "detail": "detail", "key": "key"}


@dataclass(frozen=True)
class PluginCard:
    """A card a plugin's answer shows in the chat: its type from the plugin's manifest, its words, and a key, so a later card of the same key replaces it."""

    card_type: str = ""
    label: str = ""
    tone: str = ""
    detail: str = ""
    key: str = ""

    @classmethod
    def parsed(cls, data: dict) -> "PluginCard":
        return cls(**{name: str(data[key]) for name, key in ANSWER_KEYS.items() if data.get(key) is not None})
