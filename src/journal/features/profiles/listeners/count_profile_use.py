import time

from journal.events.agent.tool_starting import ToolStarting
from journal.events.agent_listener import AgentListener
from journal.support.actor import Actor
from journal.repositories.statistics import Statistics
from journal.support.subagent_dispatch import SubagentDispatch
from journal.support.time_source import TimeSource


class CountProfileUse(AgentListener[ToolStarting]):
    """A subagent dispatched by a profile counts one use of it and when, so the profiles page reads the statistics and never the record of tool calls."""

    def __init__(self, statistics: Statistics, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.statistics = statistics

    def handle(self, event: ToolStarting) -> None:
        name = event.call.operation.role if isinstance(event.call.operation, SubagentDispatch) else ""
        if not name:
            return
        actor = Actor.agent(event.session)
        self.statistics.incremented(f"profiles.{name}.uses", actor)
        self.statistics.set(f"profiles.{name}.last_used", int(self.time_source.seconds()), actor)
