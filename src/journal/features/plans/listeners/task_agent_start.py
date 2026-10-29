from journal.events.listener import Listener
from journal.events.rows.task_started import TaskStarted
from journal.features.plans.support.task_agents import TaskAgents


class TaskAgentStart(Listener[TaskStarted]):
    """A task outside every plan that the main agent starts goes to an agent of its own while Plan agents are on."""

    def __init__(self, agents: TaskAgents) -> None:
        self.agents = agents

    def handle(self, event: TaskStarted) -> None:
        self.agents.started(event)
