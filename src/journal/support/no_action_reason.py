from journal.models.model import Model
from journal.support.rejection import Rejection


class NoActionReason:
    """The reason a row needs no action, which signing it off must carry."""

    @staticmethod
    def checked(row: Model, reason: str) -> str:
        if not reason.strip():
            raise Rejection(f"{row.noun()} {row.id} is signed off with the reason it needs no action: --why \"<why>\"")
        return reason.strip()
