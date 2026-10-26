from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.compacting import Compacting
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.models.agent import Agent
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.code_files import CodeFiles
from journal.support.recorded_call import RecordedCall
from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.features.workers.workers_options import WorkersOptions


class ToolUses:
    """One tool-use counter per session, stored on the agent's row and carried on every tool event: a plain tool use of the agent's own moves it by one as its ToolStarting is placed; a journal command and a subagent's tool use leave it where it is and carry the unchanged number; a compaction sets it back to zero, with the inbox mark, since the agent after it is as good as new. An edit of a code file by the agent itself moves its count of code edits by one too. A plain tool use also carries how many times the agent has run its command's shape, counted here once for every listener."""

    def __init__(self, agents: Agents, entries: Entries, settings: SettingRows) -> None:
        self.agents, self.entries, self.settings = agents, entries, settings

    def counted(self, event: AgentEvent) -> AgentEvent:
        if not isinstance(event, (ToolStarting, ToolFinished, Compacting)):
            return event
        rows = self.agents.session_rows(event.session)
        if not rows:
            return event
        if isinstance(event, Compacting):
            self.agents.save(rows[0].compacted(), Actor.system())
            return event
        return self.tool_counted(event, rows[0])

    def tool_counted(self, event: AgentEvent, agent: Agent) -> AgentEvent:
        if not isinstance(event, ToolStarting) or event.subagent:
            return event.counted(agent.tool_uses)
        call = event.call.recorded()
        reviewed = self.reviewed(agent.with_handover(event.time) if ToolUseCounts.is_handover(call) else agent, event)
        if event.call.is_journal:
            return event.counted(self.agents.save(reviewed, Actor.system()).tool_uses)
        agent = self.agents.save(self.used(reviewed, call, event.time), Actor.system())
        return event.counted(agent.tool_uses).shape_counted(self.entries.shape_count(event.session, call.shape) + 1 if call.shape else 0)

    def reviewed(self, agent: Agent, event: ToolStarting) -> Agent:
        call = event.call.recorded()
        return agent.briefed() if ToolUseCounts.is_handover(call) and ToolUseCounts.is_complete_brief(call) else agent

    def used(self, agent: Agent, call: RecordedCall, time: float) -> Agent:
        mode = str(self.settings.option(WorkersOptions.MODE))
        agent = agent.in_mode(mode).tool_used()
        agent = agent.code_edited() if CodeFiles.has_code(call.edited_paths) else agent
        agent = agent.file_edited() if call.edited_paths else agent
        agent = agent.lines_edited(call.operation.changed_lines()[0], time, time - self.settings.decimal(WorkersOptions.SERIES_HOURS) * 3600) if CodeFiles.has_code(call.edited_paths) else agent
        agent = agent.task_filed() if ToolUseCounts.is_task_addition(call) else agent
        agent = agent.task_completed() if ToolUseCounts.is_task_completion(call) else agent
        agent = agent.subagent_dispatched() if ToolUseCounts.is_subagent_dispatch(call) else agent
        return agent.researched() if ToolUseCounts.is_research(call) else agent
