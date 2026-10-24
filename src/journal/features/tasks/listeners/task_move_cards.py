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

# what each move of a task is called on its mark, with its tone, its icon and the field of the task that says why
MOVES = {
    "started": ("Started", "", "todos", ""),
    "resumed": ("Resumed", "", "todos", ""),
    "unblocked": ("Unblocked", "", "todos", ""),
    "done": ("Finished", "good", "todos", "outcome"),
    "paused": ("Paused", "paused", "pause", "pause_reason"),
    "blocked": ("Blocked", "warn", "todos", "block_reason"),
}


class TaskMoveCards(Listener[RowEvent]):
    """A task started, resumed, finished, paused, blocked or unblocked is one small mark in the chat, as a filed one is, naming the task and why it moved; a task given back by its worker is named by the worker's own mark instead."""

    def __init__(self, cards: MomentCards, tasks: Tasks, scope: Scope) -> None:
        self.cards, self.tasks, self.scope = cards, tasks, scope

    def handle(self, event: RowEvent) -> None:
        if isinstance(event, TaskStarted):
            self.show_move(event, "resumed" if event.prior_state == TaskState.PAUSED else "started", "")
        if isinstance(event, TaskClosed) and event.outcome in MOVES:
            self.show_move(event, event.outcome, "")
        if isinstance(event, TaskReopened) and not isinstance(event, TaskReleased):
            self.show_move(event, "unblocked", event.reason)

    def show_move(self, event: TaskStarted | TaskClosed | TaskReopened, move: str, reason: str) -> None:
        heading, tone, icon, reason_field = MOVES[move]
        with self.scope.environment(event.environment_id):
            task = self.tasks.find(event.task_id)
        label = CardDetail.shortened(f"{heading} task {task.id}: {task.title}")
        detail = reason or (getattr(task, reason_field) if reason_field else "")
        self.cards.show(event.environment_id, None, label, icon, tone=tone, detail=detail, row=Ref("tasks", task.id), actor=Actor.system(), shows=CardKind.TASK_MOVES)
