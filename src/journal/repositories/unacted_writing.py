from journal.db.query import Query
from journal.models.link import Link
from journal.models.message import Message
from journal.repositories.doc_revisions import REVISION_LINK

# a row changed sooner than this after it was written is unchanged since
UNCHANGED_SECONDS = 1


class UnactedWriting:
    """What documents and reports share: the ones not signed off, unchanged since they were written and in no link but a document's own revisions and the mentions of the journal's own chat cards, read a page at a time after a number, oldest first, with only when they were written and changed."""

    def unacted(self, last_id: int, rows: int) -> list:
        candidates = self.unsigned_query()
        links = Query.build(Link)
        cards = Query.build(Message).filter_present("data->card_type").filter_named(links, "source")
        touching = links.filter_alternatives(links.filter_ref("source", candidates), links.filter_ref("target", candidates)).filter_unequal("kind", REVISION_LINK).filter_absent(cards)
        unacted = candidates.filter_lasting_less("created_at", "updated_at", UNCHANGED_SECONDS).filter_absent(touching)
        return self.selected(unacted.filter_greater("id", last_id).with_columns("created_at", "updated_at").order("id").limit(rows))
