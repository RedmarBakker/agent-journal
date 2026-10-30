from dataclasses import dataclass

from journal.models.library_item import LibraryItem
from journal.models.support.ref import Ref


@dataclass(frozen=True)
class LibraryCopy:
    """A copy here of a library item: the item's kind and name, the version it came from, and where the copy is, a row written as sequences:12 or a profile's file path."""

    item_type: str
    name: str
    version: int
    place: str

    @classmethod
    def create(cls, item: LibraryItem, refs: list[Ref]) -> "LibraryCopy":
        return cls(item.item_type, item.name, item.version, item.file_path if item.file_path is not None else str(refs[0]))
