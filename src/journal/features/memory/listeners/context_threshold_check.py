from journal.events.agent.agent_event import AgentEvent
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.repositories.agents import Agents
from journal.features.memory.memory_thresholds import MemoryThresholds
from journal.events.blocking import Blocking


class ContextThresholdCheck(AgentListener[AgentEvent]):
    """When the context crosses a mark the agent has not handled yet, the mark is recorded as handled and as pending a decision on its row, and the memory conduct tells the agent to decide; a reading under the highest mark handled, as after a compaction, starts the marks again, so each is reached in the new window."""

    blocking = Blocking.NEXT_DECISION

    def __init__(self, agents: Agents) -> None:
        self.agents = agents

    def handle(self, event: AgentEvent) -> None:
        if event.context is None or not event.session or event.subagent:
            return
        agent = self.agents.session_agent(event.session)
        if MemoryThresholds.reached(event.context) < agent.context_threshold:
            agent = self.agents.touch(agent, Actor.system(), context_threshold=0, threshold_due=0)
        threshold = MemoryThresholds.due(event.context, agent.context_threshold)
        if threshold:
            self.agents.touch(agent, Actor.system(), context_threshold=threshold, threshold_due=threshold)
