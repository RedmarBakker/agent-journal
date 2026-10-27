from datetime import datetime
from journal.db.connection import Connection
from journal.db.query import Query
from journal.events.bus import Bus
from journal.models.link import Link
from journal.models.memory import LIGHTEST, Memory
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.repository import MATCH_ROWS, PAGE_ROWS
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

UNSHOWN_COLUMNS = ("keywords", "creator", "updater", "created_at", "updated_at")
OWNER_LINK = "owner"


class Memories(ScopedRepository[Memory]):
    """The environment's memories, each its owner's alone: the main agent's link to no row, a helper's link to its own row by an owner link; an owner's still shown, heaviest first, and the fading of an owner's every one by one at its compaction. An owner of None is the main agent."""

    model = Memory

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, time_source: TimeSource) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.links = links

    def added(self, memory: Memory, owner: Ref | None, actor: Actor) -> Memory:
        saved = self.save(memory, actor)
        if owner is not None:
            self.links.save(Link(source=Ref.build(saved), target=owner, kind=OWNER_LINK), actor)
        return saved

    def shown(self, owner: Ref | None = None) -> list[Memory]:
        return self.selected(self.shown_query(owner).without(*UNSHOWN_COLUMNS).order_descending("weight").limit(PAGE_ROWS))

    def shown_count(self, owner: Ref | None = None) -> int:
        return self.counted(self.shown_query(owner))

    def ending_with(self, row: str) -> list[Memory]:
        return self.selected(self.query().filter(expiry_row=row).filter_null("removed_at").order("id"))

    def expired(self, moment: datetime) -> list[Memory]:
        return self.selected(self.query().filter_present("expires_at").filter_less_equal("expires_at", moment).filter_null("removed_at").order("id"))

    def fade_all(self, owner: Ref | None, actor: Actor) -> list[Memory]:
        return [self.save(memory.faded(), actor) for memory in self.selected(self.shown_query(owner))]

    def removed_since(self, owner: Ref | None, since: datetime | None) -> list[Memory]:
        removed = self.owned_query(owner).filter_present("removed_at")
        return self.selected((removed if since is None else removed.filter_greater("removed_at", since)).order("id"))

    def owned_numbered(self, ids: list[int], owner: Ref | None) -> list[Memory]:
        rows = {row.id: row for row in self.selected(self.owned_query(owner).filter_listed("id", ids))}
        return [rows[n] for n in ids if n in rows]

    def search(self, terms: list[str], limit: int = MATCH_ROWS) -> list[Memory]:
        return self.search_rows(self.owned_query(None).filter_null("removed_at"), terms, limit)

    def shown_query(self, owner: Ref | None = None) -> Query:
        return self.owned_query(owner).filter_greater("weight", LIGHTEST).filter_null("removed_at")

    def owned_query(self, owner: Ref | None) -> Query:
        owner_links = self.links.query().filter(kind=OWNER_LINK).filter_ref("source", self.query())
        return self.query().filter_absent(owner_links) if owner is None else self.query().filter_existing(owner_links.filter(target=owner))
