from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.library_item import LibraryItem
from journal.models.link import Link
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.repository import Repository
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

IMPORTED_LINK = "imported_as"


class LibraryItems(Repository[LibraryItem]):
    """The items imported from the team's library, one row each by its library, type and name, each joined to the local row it became by an imported_as link."""

    model = LibraryItem

    def __init__(self, connection: Connection, bus: Bus, links: Links, time_source: TimeSource) -> None:
        super().__init__(connection, bus, time_source)
        self.links = links

    def imported(self, library_key: str, item_type: str, name: str) -> LibraryItem | None:
        rows = self.selected(self.query().filter(library_key=library_key, item_type=item_type, name=name).order("id").limit(1))
        return rows[0] if rows else None

    def library_rows(self, library_key: str) -> list[LibraryItem]:
        return self.selected(self.query().filter(library_key=library_key).order("id"))

    def joined(self, item: LibraryItem, row: Model, actor: Actor) -> None:
        self.links.save(Link(source=Ref.build(item), target=Ref.build(row), link_type=IMPORTED_LINK), actor)

    def local_rows(self, item: LibraryItem) -> list[Ref]:
        return self.links.targets(item, IMPORTED_LINK)
