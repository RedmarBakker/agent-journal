from datetime import datetime

from journal.models.reader_report import CLEARED_VERDICT, ReaderReport
from journal.repositories.scoped_repository import ScopedRepository

# the newest reports looked at for what an agent still owes
RECENT_REPORTS = 20
# the newest dismissed reports counted for a finding the agent keeps dismissing
DISMISSED_REPORTS = 200


class ReaderReports(ScopedRepository[ReaderReport]):
    model = ReaderReport

    def open_with_finding(self, command: str, finding: str) -> list[ReaderReport]:
        return [report for report in self.selected(self.query().filter(command=command).filter_null("dismissal").order("id")) if any(finding in text for text in report.findings)]

    def open_with_output_finding(self, output: int, finding: str) -> list[ReaderReport]:
        return [report for report in self.selected(self.query().filter(output=output).order("id")) if any(finding in text for text in report.findings)]

    def unread(self, session: str, locked: list[str]) -> list[ReaderReport]:
        return self.selected(self.query().filter(session=session).filter_unlisted("reader", locked).filter_null("dismissal").filter_null("read_at").order_descending("id").limit(RECENT_REPORTS))

    def reader_counts(self) -> dict[str, int]:
        return self.grouped_counts(self.query(), "reader")

    def dismissed_reports(self, earliest: datetime) -> list[ReaderReport]:
        return self.selected(self.query().filter(is_refuted=False).filter_unequal("verdict", CLEARED_VERDICT).filter_present("dismissal").filter_greater_equal("created_at", earliest).order_descending("id").limit(DISMISSED_REPORTS))

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
