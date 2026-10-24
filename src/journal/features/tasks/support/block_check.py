from journal.engine.clock import Clock
from journal.models.task_state import TaskState
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.rejection import Rejection
from journal.features.tasks.tasks_options import TasksOptions

WAIT_REFUSAL = "task {n} is work going on here, {state}, so a task waiting on it is not blocked: hand it to the worker with journal worker queue <n> {task}, or leave it open until task {n} is done"
BATCH_REFUSAL = "{count} tasks were blocked in the last {minutes} minutes: blocked is for a task that cannot move for something outside your hands; queue it to a worker with journal worker queue, pause a started task with journal task pause, or leave it open"


class BlockCheck:
    """Refuses a block that is no block, so blocked keeps meaning a task that cannot move for something outside the agent's hands: one waiting on a task this side is doing, started or delegated, and the third block in a short stretch, which is clearing the list."""

    def __init__(self, tasks: Tasks, settings: SettingRows, clock: Clock) -> None:
        self.tasks, self.settings, self.clock = tasks, settings, clock

    def refuse(self, task: int, waits: list[str]) -> None:
        for wait in waits:
            table, _, number = wait.partition(":")
            target = self.tasks.find(int(number)) if table == "task" and number.isdigit() else None
            if target is not None and target.state in (TaskState.STARTED, TaskState.DELEGATED):
                raise Rejection(WAIT_REFUSAL.format(n=target.id, state=target.state, task=task))
        self.refuse_batch()

    def refuse_batch(self) -> None:
        seconds = self.settings.integer(TasksOptions.BLOCK_BATCH)
        blocked = self.tasks.block_batch(self.clock.time() - seconds)
        if len(blocked) >= 2:
            raise Rejection(BATCH_REFUSAL.format(count=len(blocked), minutes=seconds // 60))
