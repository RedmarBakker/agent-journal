from journal.chat.moment_cards import MomentCards
from journal.chat.card_detail import CardDetail
from journal.events.listener import Listener
from journal.events.rows.row_event import RowEvent
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_edited import TaskEdited
from journal.events.rows.task_opened import TaskOpened
from journal.events.rows.task_reopened import TaskReopened
from journal.events.rows.task_released import TaskReleased
from journal.events.rows.task_started import TaskStarted
from journal.models.support.ref import Ref
from journal.models.task_state import TaskState
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.card_type import CardType
from journal.support.row_labels import RowLabels

# what each move of a task is called on its card, the card kind it is shown as and the field of the task that says why
MOVES = {
    "created": ("Created", CardType.TASK_MOVES, ""),
    "edited": ("Edited", CardType.TASK_MOVES, ""),
    "started": ("Started", CardType.TASK_MOVES, ""),
    "resumed": ("Resumed", CardType.TASK_MOVES, ""),
    "unblocked": ("Unblocked", CardType.TASK_MOVES, ""),
    "completed": ("Completed", CardType.TASK_MOVES, "outcome"),
    "paused": ("Paused", CardType.TASK_PAUSES, "pause_reason"),
    "blocked": ("Blocked", CardType.TASK_PAUSES, "block_reason"),
}


class TaskMoveCards(Listener[RowEvent]):
    """A task created, edited, started, resumed, completed, paused, blocked or unblocked is one small mark in the chat, as a filed one is, naming the task, with its team when it is a hub task, and why it moved, in the chat of every environment the task is bound to as well as its own; a task given back by its worker, or closed by the merge of its work, is named by the worker's own mark instead."""

    def __init__(self, cards: MomentCards, tasks: Tasks, scope: Scope, labels: RowLabels) -> None:
        self.cards, self.tasks, self.scope, self.labels = cards, tasks, scope, labels

    def handle(self, event: RowEvent) -> None:
        if isinstance(event, TaskOpened):
            self.show_move(event, event.row_id, "created", "")
        if isinstance(event, TaskEdited):
            self.show_move(event, event.task_id, "edited", "")
        if isinstance(event, TaskStarted):
            self.show_move(event, event.task_id, "resumed" if event.prior_state == TaskState.PAUSED else "started", "")
        if isinstance(event, TaskClosed) and event.outcome in MOVES and not event.worker_id:
            self.show_move(event, event.task_id, event.outcome, "")
        if isinstance(event, TaskReopened) and not isinstance(event, TaskReleased):
            self.show_move(event, event.task_id, "unblocked", event.reason)

    def show_move(self, event: RowEvent, task_id: int, move: str, reason: str) -> None:
        heading, shows, reason_field = MOVES[move]
        with self.scope.environment(event.environment_id):
            task = self.tasks.find(task_id)
        label = CardDetail.shortened(f"{heading} {self.labels.name('task', task)}: {task.title}")
        detail = reason or (getattr(task, reason_field) if reason_field else "")
        for environment_id in event.environment_ids():
            self.cards.show(environment_id, None, label, detail=detail, row=Ref("tasks", task.id), actor=Actor.system(), shows=shows)
