from datetime import datetime, timezone

from journal.repositories.agents import Agents
from journal.support.caller import Caller
from journal.support.time_source import TimeSource


class ThresholdDecisions:
    """The agent's decision at a context threshold, stored when it adds, weighs or removes a memory or says nothing needs keeping, which lifts the threshold's block."""

    def __init__(self, agents: Agents, time_source: TimeSource) -> None:
        self.agents, self.time_source = agents, time_source

    def decided(self, caller: Caller) -> None:
        if not caller.has_agent_row():
            return
        agent = self.agents.newest_row(caller.agent_row)
        if agent.threshold_due:
            self.agents.save(agent.context_decided(self.time_source.moment().timestamp()), caller.actor)
