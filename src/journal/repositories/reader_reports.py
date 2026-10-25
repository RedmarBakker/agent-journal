from datetime import datetime

from journal.models.reader_report import ReaderReport
from journal.repositories.scoped_repository import ScopedRepository

# the newest reports looked at for what an agent still owes
RECENT_REPORTS = 20
# the newest dismissed reports counted for a finding the agent keeps dismissing
DISMISSED_REPORTS = 200


class ReaderReports(ScopedRepository[ReaderReport]):
    model = ReaderReport

    def unread(self, session: str) -> list[ReaderReport]:
        return self.selected(self.query().filter(session=session).filter_null("dismissal").filter_null("read_at").order_descending("id").limit(RECENT_REPORTS))

    def dismissed_reports(self, earliest: datetime) -> list[ReaderReport]:
        return self.selected(self.query().filter(is_refuted=False).filter_present("dismissal").filter_greater_equal("created_at", earliest).order_descending("id").limit(DISMISSED_REPORTS))

    def unrevised(self, session: str, revisions: dict[str, datetime]) -> list[ReaderReport]:
        unchanged = [self.query().filter(reader=reader).filter_greater_equal("read_at", revision) for reader, revision in revisions.items()]
        if not unchanged:
            return []
        query = self.query().filter(session=session, is_refuted=False).filter_null("dismissal").filter_present("read_at").filter_alternatives(*unchanged)
        return self.selected(query.order_descending("id").limit(RECENT_REPORTS))

    def refuted(self, session: str, revisions: dict[str, datetime]) -> list[ReaderReport]:
        unchanged = [self.query().filter(reader=reader).filter_greater_equal("judged_at", revision) for reader, revision in revisions.items()]
        if not unchanged:
            return []
        query = self.query().filter(session=session, is_refuted=True).filter_alternatives(*unchanged)
        return self.selected(query.order_descending("id").limit(RECENT_REPORTS))
