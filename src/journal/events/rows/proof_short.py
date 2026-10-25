from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent
from journal.support.actor import Actor
from journal.support.actor_kind import ActorKind


@dataclass(frozen=True, kw_only=True)
class ProofShort(RowEvent):
    """A proof was checked and found short, by the agent or by the journal's reviewer: what is missing goes back to the worker that holds the task."""

    task_id: int
    worker_id: int
    point: int
    shortfall: str
    dispatcher: str = ""
    earlier: tuple[str, ...] = ()

    def is_reviewers(self) -> bool:
        return bool(self.actor) and Actor.parse(self.actor).kind == ActorKind.REVIEWER
