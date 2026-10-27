from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.worker_queue_drained import WorkerQueueDrained
from journal.events.rows.worker_rebased import WorkerRebased
from journal.events.rows.worker_retired import WorkerRetired
from journal.events.rows.worker_sent_on import WorkerSentOn
from journal.events.rows.worker_reused import WorkerReused
from journal.events.rows.worker_revived import WorkerRevived
from journal.support.actor import Actor
from journal.support.card_type import CardType
from journal.chat.moment_cards import MomentCards
from journal.chat.card_detail import CardDetail
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks

MOMENTS = {
    WorkerReused: ("sent its next job", "brief"),
    WorkerRevived: ("started again in its last session", "brief"),
    WorkerRetired: ("retired, its report acted on", ""),
    WorkerQueueDrained: ("its queue given back", "tasks"),
    WorkerRebased: ("rebased by the journal", "outcome"),
}


class WorkerMomentCards(Listener[RowEvent]):
    """Each moment of a worker after its dispatch is one new mark in the chat naming the task the worker holds: sent its next job, started again, retired, its queue given back, rebased by the journal; a message sent to it is the worker chat's."""

    def __init__(self, cards: MomentCards, tasks: Tasks) -> None:
        self.cards, self.tasks = cards, tasks

    def handle(self, event: RowEvent) -> None:
        if not isinstance(event, (WorkerReused, WorkerRevived, WorkerRetired, WorkerQueueDrained, WorkerRebased)) or isinstance(event, WorkerSentOn):
            return
        text, detail = MOMENTS[type(event)]
        worker = event.worker
        actor = Actor.agent(worker.dispatcher) if worker.dispatcher else Actor.system()
        label = CardDetail.shortened(f"{worker.name}: {text}")
        row = Ref("workers", worker.id)
        data = {"kind": "card", "row": str(row), "command": "", "task": self.tasks.last_task_id(row)}
        self.cards.show_fields(event.environment_id, worker.dispatcher, label, data, actor, CardType.WORKER_STEPS, getattr(event, detail) if detail else "")
