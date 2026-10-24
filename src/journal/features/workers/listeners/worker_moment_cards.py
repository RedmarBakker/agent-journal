from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.worker_notified import WorkerNotified
from journal.events.rows.worker_queue_drained import WorkerQueueDrained
from journal.events.rows.worker_retired import WorkerRetired
from journal.events.rows.worker_reused import WorkerReused
from journal.events.rows.worker_revived import WorkerRevived
from journal.support.actor import Actor
from journal.support.card_kind import CardKind
from journal.chat.moment_cards import MomentCards
from journal.chat.card_detail import CardDetail
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks

MOMENTS = {
    WorkerReused: ("sent its next job", "", "brief"),
    WorkerRevived: ("started again in its last session", "", "brief"),
    WorkerNotified: ("sent a message in its session", "", "text"),
    WorkerRetired: ("retired, its report acted on", "good", ""),
    WorkerQueueDrained: ("its queue given back", "", "tasks"),
}


class WorkerMomentCards(Listener[RowEvent]):
    """Each moment of a worker after its dispatch is one new mark in the chat with its own tone, naming the task the worker holds: sent its next job, started again, sent a message, retired, its queue given back."""

    def __init__(self, cards: MomentCards, tasks: Tasks) -> None:
        self.cards, self.tasks = cards, tasks

    def handle(self, event: RowEvent) -> None:
        if not isinstance(event, (WorkerReused, WorkerRevived, WorkerNotified, WorkerRetired, WorkerQueueDrained)):
            return
        text, tone, detail = MOMENTS[type(event)]
        worker = event.worker
        actor = Actor.agent(worker.dispatcher) if worker.dispatcher else Actor.system()
        label = CardDetail.shortened(f"Worker {worker.id}, {worker.name}: {text}")
        row = Ref("workers", worker.id)
        data = {"kind": "card", "icon": "agents", "tone": tone, "row": str(row), "command": "", "task": self.tasks.last_task_id(row)}
        self.cards.show_fields(event.environment_id, worker.dispatcher, label, data, actor, CardKind.WORKERS, getattr(event, detail) if detail else "")
