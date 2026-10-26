from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.repositories.agents import Agents
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.models.support.ref import Ref


class PausedDeclineClearing(Listener[TaskClosed]):
    """A task closed by the agent that set its paused work aside ends that, so the next stop offers the paused work again."""

    def __init__(self, tasks: Tasks, agents: Agents) -> None:
        self.tasks, self.agents = tasks, agents

    def handle(self, event: TaskClosed) -> None:
        declined = self.agents.declined_agents()
        holder = self.tasks.task_holder(event.task_id) if declined else None
        for agent in declined:
            if holder == Ref.build(agent):
                self.agents.save(agent.paused_decline_cleared(), Actor.system())
