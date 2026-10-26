from typing import TypeVar

from journal.support.rejection import Rejection

R = TypeVar("R")


class NoActionReason:
    """Signing a row off as needing no action, which must carry the reason."""

    @staticmethod
    def signed(row: R, reason: str) -> R:
        if not reason.strip():
            raise Rejection(f"{row.noun()} {row.id} is signed off with the reason it needs no action: --why \"<why>\"")
        return row.with_(settled_reason=reason.strip())
