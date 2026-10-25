from journal.models.verifier_state import VerifierState
from journal.db.query import Query
from journal.features.verification.support.verifier_dispatch import VERIFIES
from journal.http.controllers.controller import Controller
from journal.http.support.model_fields import ModelFields
from journal.models.verifier import Verifier
from journal.repositories.links import Links
from journal.repositories.verifiers import Verifiers


class VerifierController(Controller[Verifier]):
    """The verifiers the journal sent here; one that ended without a verdict is closed. One read by id names the rows whose dismissals it judged, in order."""

    repository: Verifiers

    def __init__(self, verifiers: Verifiers, links: Links) -> None:
        self.repository, self.links = verifiers, links

    def open_rows(self, query: Query) -> Query:
        return query.filter_unequal("state", VerifierState.ENDED)

    def closed_rows(self, query: Query) -> Query:
        return query.filter(state=VerifierState.ENDED)

    def shown_page(self, rows: list[Verifier]) -> list[dict]:
        return [{**ModelFields.build(row), "judged": [str(ref) for ref in self.links.targets(row, VERIFIES)]} for row in rows]
