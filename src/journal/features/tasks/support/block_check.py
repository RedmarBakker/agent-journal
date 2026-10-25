from journal.engine.clock import Clock
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.rejection import Rejection
from journal.features.tasks.tasks_options import TasksOptions

BATCH_REFUSAL = "{count} tasks were blocked in the last {minutes} minutes: blocked is for a task that cannot move for something outside your hands; queue it to a worker with journal worker queue, pause a started task with journal task pause, or leave it open"


class BlockCheck:
    """Refuses a block that is no block, so blocked keeps meaning a task that cannot move for something outside the agent's hands: the third block in a short stretch, which is clearing the list. A task may wait on another that is open, started or delegated to a worker, and opens when that one is done."""

    def __init__(self, tasks: Tasks, settings: SettingRows, clock: Clock) -> None:
        self.tasks, self.settings, self.clock = tasks, settings, clock

    def refuse(self) -> None:
        seconds = self.settings.integer(TasksOptions.BLOCK_BATCH)
        blocked = self.tasks.block_batch(self.clock.time() - seconds)
        if len(blocked) >= 2:
            raise Rejection(BATCH_REFUSAL.format(count=len(blocked), minutes=seconds // 60))
