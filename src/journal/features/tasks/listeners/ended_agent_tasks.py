from datetime import datetime, timezone

from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.models.task_state import TaskState
from journal.repositories.agents import Agents
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor

ENDED_REASON = "the session that held it ended"


class EndedAgentTasks(AgentListener[SessionStarted]):
    """When a main session starts, a task still started in the hand of a main agent of the environment whose session has ended is paused, so the agent that starts can resume it and no task is held by a session that will never work again; a session that starts again finds a task paused for its own end started again."""

    blocking = True

    def __init__(self, tasks: Tasks, agents: Agents) -> None:
        self.tasks, self.agents = tasks, agents

    def handle(self, event: SessionStarted) -> None:
        if event.subagent:
            return
        starting = self.agents.session_agent(event.session)
        if starting.role.is_helper():
            return
        moment = datetime.fromtimestamp(event.time, timezone.utc)
        ended = self.agents.ended_main_query(event.environment_id).filter_unequal("id", starting.id)
        for task in self.tasks.agents_tasks(TaskState.STARTED, ended):
            self.tasks.save(task.paused(ENDED_REASON, moment), Actor.system())
        for task in self.tasks.agents_paused_with(ENDED_REASON, self.agents.query().filter(id=starting.id)):
            self.tasks.save(task.started(moment), Actor.system())
