from dataclasses import dataclass

from sync_server.item import Item
from sync_server.item_version import ItemVersion


@dataclass(frozen=True)
class LibraryEntry:
    """An item as the library lists it, with its latest complete version."""

    item: Item
    version: ItemVersion

    @classmethod
    def parsed(cls, fields: dict) -> "LibraryEntry":
        return cls(Item.read(fields["item"]), ItemVersion.read(fields["version"]))
