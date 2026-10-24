from datetime import datetime, timezone

from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.models.agent import Agent
from journal.models.task_state import TaskState
from journal.repositories.agents import Agents
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor

ENDED_REASON = "the session that held it ended"


class EndedAgentTasks(AgentListener[SessionStarted]):
    """When a main session starts, a task still started in the hand of a main agent of the environment whose session has ended is paused, so the agent that starts can resume it and no task is held by a session that will never work again."""

    blocking = True

    def __init__(self, tasks: Tasks, agents: Agents) -> None:
        self.tasks, self.agents = tasks, agents

    def handle(self, event: SessionStarted) -> None:
        if event.subagent:
            return
        ended = {agent.id for agent in self.agents.ended_main_agents(event.environment_id)} - {self.agents.session_agent(event.session).id}
        for task_id, holder in self.tasks.holders().items():
            if holder.type == Agent.table() and holder.id in ended:
                self.paused(task_id, event.time)

    def paused(self, task_id: int, time: float) -> None:
        task = self.tasks.find(task_id)
        if task.state == TaskState.STARTED:
            self.tasks.save(task.paused(ENDED_REASON, datetime.fromtimestamp(time, timezone.utc)), Actor.system())
