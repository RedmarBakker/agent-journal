from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class VerifierExited(RowEvent):
    """A verifier's process ended, so the verifier is free for the next judgement waiting."""

    feature_name = "verification"
