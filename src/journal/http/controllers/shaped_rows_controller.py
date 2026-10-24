from typing import TypeVar

from journal.http.controllers.controller import Controller
from journal.models.model import Model

S = TypeVar("S", bound=Model)


class ShapedRowsController(Controller[S]):
    """A controller whose rows are a chosen part of its repository's, so a read by id picks from those rows, never any row of the table."""

    def id_rows(self, ids: tuple[int, ...]) -> list[S]:
        return [row for row in self.rows() if row.row_id in ids]
