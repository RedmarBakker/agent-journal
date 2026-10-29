from journal.http.controllers.controller import Controller
from journal.models.domain_count import DomainCount
from journal.repositories.domain_counts import DomainCounts


class DomainCountController(Controller[DomainCount]):
    """The live figures of each domain, a row apiece, so the viewer's sync carries a change in them like any table's."""

    def __init__(self, counts: DomainCounts) -> None:
        self.repository = counts
