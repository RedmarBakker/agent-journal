from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent_listener import AgentListener
from journal.features.tasks.support.task_state_names import CHOOSING_PAUSED_WORK
from journal.repositories.agents import Agents
from journal.support.actor import Actor


class UserWordsDecline(AgentListener[PromptSubmitted]):
    """The user's own words while the agent chooses its paused work set that work aside until the next close: the user said what comes next."""

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: PromptSubmitted) -> None:
        agent = self.agents.newest_row(event.agent)
        if event.is_users and agent.is_top_state(CHOOSING_PAUSED_WORK):
            self.agents.rewritten(agent, Actor.system(), lambda current: current.paused_work_declined(event.time))
