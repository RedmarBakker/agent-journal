from journal.chat.moment_cards import MomentCards
from journal.chat.card_detail import CardDetail
from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_reopened import TaskReopened
from journal.events.rows.task_released import TaskReleased
from journal.events.rows.task_started import TaskStarted
from journal.models.support.ref import Ref
from journal.models.task_state import TaskState
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.card_kind import CardKind
from journal.support.row_labels import RowLabels

# what each move of a task is called on its card, the card kind it is shown as and the field of the task that says why
MOVES = {
    "started": ("Started", CardKind.TASK_MOVES, ""),
    "resumed": ("Resumed", CardKind.TASK_MOVES, ""),
    "unblocked": ("Unblocked", CardKind.TASK_MOVES, ""),
    "done": ("Finished", CardKind.TASK_MOVES, "outcome"),
    "paused": ("Paused", CardKind.TASK_PAUSES, "pause_reason"),
    "blocked": ("Blocked", CardKind.TASK_PAUSES, "block_reason"),
}


class TaskMoveCards(Listener[RowEvent]):
    """A task started, resumed, finished, paused, blocked or unblocked is one small mark in the chat, as a filed one is, naming the task, with its team when it is a hub task, and why it moved, in the chat of every environment the task is bound to as well as its own; a task given back by its worker, or closed by the merge of its work, is named by the worker's own mark instead."""

    def __init__(self, cards: MomentCards, tasks: Tasks, scope: Scope, labels: RowLabels) -> None:
        self.cards, self.tasks, self.scope, self.labels = cards, tasks, scope, labels

    def handle(self, event: RowEvent) -> None:
        if isinstance(event, TaskStarted):
            self.show_move(event, "resumed" if event.prior_state == TaskState.PAUSED else "started", "")
        if isinstance(event, TaskClosed) and event.outcome in MOVES and not event.worker_id:
            self.show_move(event, event.outcome, "")
        if isinstance(event, TaskReopened) and not isinstance(event, TaskReleased):
            self.show_move(event, "unblocked", event.reason)

    def show_move(self, event: TaskStarted | TaskClosed | TaskReopened, move: str, reason: str) -> None:
        heading, shows, reason_field = MOVES[move]
        with self.scope.environment(event.environment_id):
            task = self.tasks.find(event.task_id)
        label = CardDetail.shortened(f"{heading} {self.labels.name('task', task)}: {task.title}")
        detail = reason or (getattr(task, reason_field) if reason_field else "")
        for environment_id in event.environment_ids():
            self.cards.show(environment_id, None, label, detail=detail, row=Ref("tasks", task.id), actor=Actor.system(), shows=shows)
