from dataclasses import dataclass

from sync_server.library_entry import LibraryEntry


@dataclass(frozen=True)
class ItemListAnswer:
    """The items GET /items lists, each with its latest complete version."""

    items: list[LibraryEntry]
