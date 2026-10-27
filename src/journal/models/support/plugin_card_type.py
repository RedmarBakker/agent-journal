from dataclasses import dataclass

# the key a plugin's manifest names a card's type by, which a manifest stored here names card_type
MANIFEST_TYPE_KEY = "kind"


@dataclass(frozen=True)
class PluginCardType:
    """A type of card a plugin's manifest declares, under kind there and card_type as stored here: the label, icon and tone its cards take unless a card says its own, and whether it shows folded."""

    card_type: str
    label: str = ""
    icon: str = "plug"
    tone: str = ""
    collapsed: bool = False

    @classmethod
    def parsed(cls, data: dict) -> "PluginCardType":
        return cls(**{("card_type" if key == MANIFEST_TYPE_KEY else key): value for key, value in data.items()})
