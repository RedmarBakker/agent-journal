from journal.models.support.ref import Ref
from journal.repositories.rows import Rows
from journal.support.rejection import Rejection


class MessageReference:
    """A row a message the user sends refers to, named as command_outputs:12, such as the output asked about from its docked card, checked to be there."""

    def __init__(self, rows: Rows) -> None:
        self.rows = rows

    def checked(self, reference: object) -> Ref:
        table, _, number = str(reference).partition(":")
        if not number.isdigit() or not self.rows.is_row(Ref(table, int(number))):
            raise Rejection(f"a message refers to a row that is there, named as command_outputs:12, not {reference!r}")
        return Ref(table, int(number))
