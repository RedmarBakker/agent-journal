from datetime import datetime
from journal.models.report import UPDATE, Report
from journal.db.query import Query
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.unacted_writing import UnactedWriting


class Reports(ScopedRepository[Report], UnactedWriting):
    model = Report

    def unsigned_query(self) -> Query:
        return self.query().filter(settled_reason="").filter_null("read_at").filter_unequal("kind", UPDATE)

    def latest_update(self) -> list[Report]:
        return self.selected(self.query().filter(kind=UPDATE).order_descending("id").limit(1))

    def last_read_update(self) -> list[Report]:
        return self.selected(self.query().filter(kind=UPDATE).filter_present("read_at").order_descending("id").limit(1))

    def recent_reports(self, start: datetime, end: datetime) -> list[Report]:
        return self.selected(self.query().filter_unequal("kind", UPDATE).filter_greater_equal("created_at", start).filter_less("created_at", end).order("id"))

    def recent_numbered(self, ids: list[int], time: datetime) -> list[Report]:
        return [report for report in self.numbered(ids) if report.creation_time >= time]
