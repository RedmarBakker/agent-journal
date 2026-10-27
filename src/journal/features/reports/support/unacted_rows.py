from journal.features.reports.support.unacted_row import UnactedRow
from journal.models.model import Model
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.docs import Docs
from journal.repositories.reports import Reports
from journal.repositories.unacted_writing import UnactedWriting

# the oldest of each kind named at a time; the next are named once these are acted on
UNACTED_ROWS = 3


class UnactedRows:
    """The oldest reports and documents never acted on, three of each, read from what the journal records: not signed off, never read in the viewer or by its show command, never linked or mentioned, a document's own revisions aside, and unchanged since they were written; an update written for the user is no such report."""

    def __init__(self, reports: Reports, docs: Docs, outputs: CommandOutputs) -> None:
        self.reports, self.docs, self.outputs = reports, docs, outputs

    def rows(self) -> tuple[UnactedRow, ...]:
        return (*self.unacted("report", self.reports), *self.unacted("doc", self.docs))

    def unacted(self, type_name: str, writing: UnactedWriting) -> list[UnactedRow]:
        unacted_rows: list[UnactedRow] = []
        last_id = 0
        while len(unacted_rows) < UNACTED_ROWS:
            page = writing.unacted(last_id, UNACTED_ROWS)
            unacted_rows.extend(UnactedRow(type_name, row.row_id, row.creation_time.timestamp()) for row in page if not self.is_opened(type_name, row))
            if len(page) < UNACTED_ROWS:
                break
            last_id = page[-1].row_id
        return unacted_rows[:UNACTED_ROWS]

    def is_opened(self, type_name: str, row: Model) -> bool:
        return any(run.command.split()[:4] == ["journal", type_name, "show", str(row.row_id)] for run in self.outputs.started_with(f"journal {type_name} show {row.row_id}"))
