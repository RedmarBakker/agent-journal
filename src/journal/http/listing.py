from dataclasses import dataclass
from datetime import datetime, timezone

from journal.db.query import Query
from journal.http.row_list_page import RowListPage
from journal.repositories.repository import PAGE_ROWS as REPOSITORY_PAGE_ROWS, Repository

PAGE_ROWS = 50
# the most rows a list asks for, one under a repository's page, so the row that says another page follows fits in one read
LISTING_ROW_LIMIT = REPOSITORY_PAGE_ROWS - 1


@dataclass(frozen=True)
class Listing:
    """What the viewer requests of a list, each read in SQL within the page's row limit: the newest `limit` rows and, but on a timeline, the newest `limit` open ones besides, so no list returns more than two pages, only the closed ones when requested, older than `before`, newer than `after`, changed since `since` (newer than `after` and at most `limit` of them, so a change since an old moment never reads the whole table), or only the ids given."""

    limit: int = PAGE_ROWS
    closed: bool = False
    upper_id: int = 0
    lower_id: int = 0
    cutoff_at: float = 0.0
    ids: tuple[int, ...] = ()

    @classmethod
    def query_listing(cls, query: dict) -> "Listing":
        ids = tuple(int(n) for n in str(query.get("ids", "")).split(",") if n.strip().isdigit())
        cutoff = float(query["since"]) if query.get("since") else 0.0
        closed = str(query.get("closed", "")).lower() in ("1", "true", "yes")
        return cls(min(cls.query_number(query, "limit", PAGE_ROWS), LISTING_ROW_LIMIT), closed, cls.query_number(query, "before", 0), cls.query_number(query, "after", 0), cutoff, ids)

    @staticmethod
    def query_number(query: dict, key: str, default: int) -> int:
        return int(query[key]) if query.get(key) else default

    def listed(self, repository: Repository, rows: Query, open_rows: Query, closed_rows: Query) -> RowListPage:
        page = self.timeline(repository, rows, closed_rows)
        if self.cutoff_at or self.closed or self.upper_id:
            return page
        shown = [row.row_id for row in page["rows"]]
        open_ = repository.selected(open_rows.filter_greater("id", self.lower_id).filter_unlisted("id", shown).order_descending("id").limit(self.limit))
        return RowListPage(rows=sorted([*open_, *page["rows"]], key=lambda row: row.row_id), is_last_page=page["is_last_page"])

    def timeline(self, repository: Repository, rows: Query, closed_rows: Query) -> RowListPage:
        if self.cutoff_at:
            return self.changes(repository, rows)
        if self.closed:
            return self.newest(repository, self.older(closed_rows))
        return self.newest(repository, self.older(rows).filter_greater("id", self.lower_id))

    def changes(self, repository: Repository, rows: Query) -> RowListPage:
        return self.newest(repository, rows.filter_greater("updated_at", datetime.fromtimestamp(self.cutoff_at, timezone.utc)).filter_greater("id", self.lower_id))

    def older(self, rows: Query) -> Query:
        return rows.filter_less("id", self.upper_id) if self.upper_id else rows

    def newest(self, repository: Repository, rows: Query) -> RowListPage:
        newest = repository.selected(rows.order_descending("id").limit(self.limit + 1))
        return RowListPage(rows=sorted(newest[:self.limit], key=lambda row: row.row_id), is_last_page=len(newest) <= self.limit)
