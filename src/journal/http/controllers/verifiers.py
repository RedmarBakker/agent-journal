from journal.features.verification.support.verifier_dispatch import VERIFIES
from journal.http.controllers.shaped_rows_controller import ShapedRowsController
from journal.http.support.model_fields import ModelFields
from journal.models.verifier import Verifier
from journal.repositories.links import Links
from journal.repositories.verifiers import Verifiers


class VerifierController(ShapedRowsController[Verifier]):
    """The verifiers the journal sent here; one that ended without a verdict is closed. One read by id names the rows whose dismissals it judged, in order."""

    repository: Verifiers

    def __init__(self, verifiers: Verifiers, links: Links) -> None:
        self.repository, self.links = verifiers, links

    def rows(self) -> list[Verifier]:
        return self.repository.scoped()

    def is_open(self, row: Verifier) -> bool:
        return not row.has_ended()

    def shown_page(self, rows: list[Verifier]) -> list[dict]:
        return [{**ModelFields.build(row), "judged": [str(ref) for ref in self.links.targets(row, VERIFIES)]} for row in rows]
