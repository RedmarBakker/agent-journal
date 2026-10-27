from dataclasses import dataclass

from sync_server.item import Item
from sync_server.item_version import ItemVersion


@dataclass(frozen=True)
class ItemVersionsAnswer:
    """An item as GET /items/<type>/<name> reads it, with every complete version and its note."""

    item: Item
    versions: list[ItemVersion]
