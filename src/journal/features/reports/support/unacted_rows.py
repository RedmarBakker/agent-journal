from journal.features.reports.support.unacted_row import UnactedRow
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.doc_revisions import REVISION_LINK
from journal.repositories.docs import Docs
from journal.repositories.links import Links
from journal.repositories.reports import Reports


class UnactedRows:
    """The reports and documents never acted on, read from what the journal records: not signed off, never read in the viewer or by its show command, never linked or mentioned, a document's own revisions aside, and unchanged since they were written; an update written for the user is no such report."""

    def __init__(self, reports: Reports, docs: Docs, links: Links, outputs: CommandOutputs) -> None:
        self.reports, self.docs, self.links, self.outputs = reports, docs, links, outputs

    def rows(self) -> tuple[UnactedRow, ...]:
        written = [("report", row) for row in self.reports.unsettled()] + [("doc", row) for row in self.docs.unsettled()]
        unchanged = [(kind, row) for kind, row in written if (row.update_time - row.creation_time).total_seconds() < 1]
        linked = {ref for link in self.links.touching_any([row for _, row in unchanged]) if link.kind != REVISION_LINK for ref in (link.source, link.target)}
        return tuple(UnactedRow(kind, row.row_id, row.creation_time.timestamp()) for kind, row in unchanged if Ref.build(row) not in linked and not self.is_opened(kind, row))

    def is_opened(self, kind: str, row: Model) -> bool:
        return any(run.command.split()[:4] == ["journal", kind, "show", str(row.row_id)] for run in self.outputs.started_with(f"journal {kind} show {row.row_id}"))
