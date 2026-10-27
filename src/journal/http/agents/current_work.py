from dataclasses import dataclass

from journal.engine.states_catalogue import StatesCatalogue
from journal.models.agent import Agent
from journal.models.task import Task
from journal.support.missing_row import MissingRow
from journal.repositories.tasks import Tasks


@dataclass(frozen=True)
class AgentWork:
    """The task an agent has in hand and, while it is paused on top of it, what it waits for."""

    task: Task
    wait_text: str = ""
    wait_refs: str = ""


class CurrentWork:
    """Reads an agent's stack down through its waits to its current task: the viewer's status line names the task, or "Waiting for …" while a wait is on top of it, from the topmost wait that names what it waits for."""

    def __init__(self, states: StatesCatalogue, tasks: Tasks) -> None:
        self.states, self.tasks = states, tasks

    def work(self, agent: Agent) -> AgentWork | None:
        task_id = next((layer.task_number() for layer in reversed(self.states.stack(agent).states) if layer.task_number()), 0)
        if not task_id:
            return None
        try:
            return AgentWork(self.tasks.find(task_id), *self.wait_text(agent))
        except MissingRow:
            return None

    def wait_text(self, agent: Agent) -> tuple[str, str]:
        layers = self.states.stack(agent).states
        return next((layer.wait_description() for layer in reversed(layers) if layer.wait_description()[0]), ("", ""))
