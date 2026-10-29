from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.features.plans.support.task_agents import TaskAgents


class TaskAgentFinish(Listener[TaskClosed]):
    """A task worked by an agent of its own stops that agent when it closes; its environment, row and link stay."""

    def __init__(self, agents: TaskAgents) -> None:
        self.agents = agents

    def handle(self, event: TaskClosed) -> None:
        self.agents.stopped(event)
