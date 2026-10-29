from dataclasses import dataclass
from typing import ClassVar

from journal.models.model import Model


@dataclass(frozen=True)
class LibraryItem(Model):
    """An item imported from the team's library, kept on this machine alone: which library, the item's type and name, the version imported, and its portable body as imported, so a later edit of the local copy can be named, its hash worked out by the library feature's PortableBody; the local row it became is joined by an imported_as link, a file kind's copy by its path."""

    shared: ClassVar[bool] = False

    library_key: str = ""
    item_type: str = ""
    name: str = ""
    version: int = 0
    body: str = ""
    file_path: str | None = None

    def title_words(self) -> str:
        return f"{self.item_type} {self.name}, version {self.version}"
