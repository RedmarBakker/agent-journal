from dataclasses import dataclass
from journal.events.rows.worker_mention import WorkerMention

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class WorkerModelJudged(RowEvent):
    """A verifier the journal sent judged whether a worker's model fit its merged work: too strong, right or too weak, with its reason and the verifier's session, which the verdict ends."""

    feature_name = "verification"

    worker: WorkerMention
    verdict: str
    reason: str
    verifier_session: str
