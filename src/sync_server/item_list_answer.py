from dataclasses import dataclass

from sync_server.library_entry import LibraryEntry


@dataclass(frozen=True)
class ItemListAnswer:
    """The items GET /items lists, each with its latest complete version."""

    items: list[LibraryEntry]

    @classmethod
    def parsed(cls, fields: dict) -> "ItemListAnswer":
        return cls([LibraryEntry.parsed(entry) for entry in fields["items"]])
