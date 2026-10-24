from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.compacting import Compacting
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.models.agent import Agent
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.support.actor import Actor
from journal.support.code_files import CodeFiles
from journal.support.recorded_call import RecordedCall
from journal.features.workers.support.tool_use_counts import ToolUseCounts


class ToolUses:
    """One tool-use counter per session, stored on the agent's row and carried on every tool event: a plain tool use of the agent's own moves it by one as its ToolStarting is placed; a journal command and a subagent's tool use leave it where it is and carry the unchanged number; a compaction sets it back to zero, with the inbox mark, since the agent after it is as good as new. An edit of a code file by the agent itself moves its count of code edits by one too. A plain tool use also carries how many times the agent has run its command's shape, counted here once for every listener."""

    def __init__(self, agents: Agents, entries: Entries) -> None:
        self.agents, self.entries = agents, entries

    def counted(self, event: AgentEvent) -> AgentEvent:
        if not isinstance(event, (ToolStarting, ToolFinished, Compacting)):
            return event
        rows = self.agents.global_matching(session=event.session)
        if not rows:
            return event
        if isinstance(event, Compacting):
            self.agents.save(rows[0].compacted(), Actor.system())
            return event
        return self.tool_counted(event, rows[0])

    def tool_counted(self, event: AgentEvent, agent: Agent) -> AgentEvent:
        if isinstance(event, ToolStarting) and not event.subagent and ToolUseCounts.is_handover(event.call.recorded()):
            agent = self.agents.save(agent.with_handover(event.time), Actor.system())
        if isinstance(event, ToolStarting) and not event.call.is_journal and not event.subagent:
            agent = self.agents.save(self.used(agent, event.call.recorded()), Actor.system())
            shape = event.call.recorded().shape
            return event.counted(agent.tool_uses).shape_counted(self.entries.shape_count(event.session, shape) + 1 if shape else 0)
        return event.counted(agent.tool_uses)

    @staticmethod
    def used(agent: Agent, call: RecordedCall) -> Agent:
        agent = agent.tool_used()
        agent = agent.code_edited() if CodeFiles.has_code(call.edited_paths) else agent
        agent = agent.file_edited() if call.edited_paths else agent
        agent = agent.subagent_dispatched() if ToolUseCounts.is_subagent_dispatch(call) else agent
        return agent.researched() if ToolUseCounts.is_research(call) else agent
