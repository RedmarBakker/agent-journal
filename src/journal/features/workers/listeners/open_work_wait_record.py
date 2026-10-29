from journal.events.listener import Listener
from journal.engine.stack_moved import StackMoved
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor


class OpenWorkWaitRecord(Listener[StackMoved]):
    """The seconds a wait removed from the stack counts against the agent, past its uncounted ones and only when it opened beside other work, kept on the agent's row."""

    def __init__(self, agents: Agents, settings: SettingRows) -> None:
        self.agents, self.settings = agents, settings

    def handle(self, event: StackMoved) -> None:
        seconds = event.counted_wait_seconds(self.settings.integer(TasksOptions.UNCOUNTED_WAIT_SECONDS))
        if not seconds:
            return
        cutoff = event.moved_at - self.settings.decimal(WorkersOptions.SERIES_HOURS) * 3600
        self.agents.rewritten(event.agent, Actor.system(), lambda current: current.open_work_waited(seconds, event.moved_at, cutoff))
