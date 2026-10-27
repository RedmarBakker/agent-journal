from journal.models.all_models import AllModels
from journal.models.support.commentable import Commentable
from journal.models.support.ref import Ref
from journal.repositories.rows import Rows
from journal.support.rejection import Rejection

# the rows a message may be written under as a comment, those of every Commentable model; one under a chat message is a reply to it
COMMENTED = tuple(model.table() for model in AllModels.MODELS if issubclass(model, Commentable))
REPLIED = "messages"


class CommentTarget:
    """The row a comment is written under, named as tasks:12, checked to be one that takes comments and is there."""

    def __init__(self, rows: Rows) -> None:
        self.rows = rows

    def checked(self, reference: object) -> Ref:
        matched = str(reference)
        table, _, number = matched.partition(":")
        if table not in COMMENTED or not number.isdigit() or not self.rows.is_row(Ref(table, int(number))):
            raise Rejection(f"a comment goes under a row that exists, named like tasks:12, not {matched!r}")
        return Ref(table, int(number))
