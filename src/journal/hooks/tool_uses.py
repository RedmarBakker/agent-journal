from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.compacting import Compacting
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.models.agent import Agent
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.code_files import CodeFiles
from journal.support.recorded_call import RecordedCall
from journal.features.workers.support.tool_use_counts import ToolUseCounts
from journal.features.workers.workers_options import WorkersOptions
from journal.features.workers.support.test_run_folder import TestRunFolder
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_line import WorkerLine
from journal.support.tool_call import ToolCall

# how long a clocked-out worker or an open task with a free place may wait for the orchestrator before the tool uses made meanwhile count against it
ANSWER_SECONDS = 300
# the worker command that takes a worker's work in
MERGE_VERB = "merge"


class ToolUses:
    """One tool-use counter per session, stored on the agent's row and carried on every tool event: a plain tool use of the agent's own moves it by one as its ToolStarting is placed; a journal command and a subagent's tool use leave it where it is and carry the unchanged number; a compaction sets it back to zero, with the inbox mark, since the agent after it is as good as new. An edit of a code file by the agent itself moves its count of code edits by one too. A plain tool use also carries how many times the agent has run its command's shape, counted here once for every listener."""

    def __init__(self, agents: Agents, entries: Entries, settings: SettingRows, tasks: Tasks, workers: Workers, branch: WorkerBranch, runs: TestRunFolder) -> None:
        self.agents, self.entries, self.settings, self.tasks, self.workers, self.branch, self.runs = agents, entries, settings, tasks, workers, branch, runs

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
        if isinstance(event, ToolStarting) and not event.subagent and ToolUseCounts.is_handover(event.call.recorded()):
            agent = self.agents.save(agent.with_handover(event.time), Actor.system())
        if isinstance(event, ToolStarting) and not event.subagent:
            agent = self.agents.save(self.reviewed(agent, event), Actor.system())
        if isinstance(event, ToolStarting) and not event.call.is_journal and not event.subagent:
            agent = self.agents.save(self.used(agent, event.call.recorded(), event.time), Actor.system())
            shape = event.call.recorded().shape
            return event.counted(agent.tool_uses).shape_counted(self.entries.shape_count(event.session, shape) + 1 if shape else 0)
        return event.counted(agent.tool_uses)

    def reviewed(self, agent: Agent, event: ToolStarting) -> Agent:
        call = event.call.recorded()
        agent = self.merged(agent, event.call) if ToolUseCounts.is_merge(call) else agent
        agent = agent.proof_read() if ToolUseCounts.is_proof_read(call) else agent
        tested = self.runs.folder(event.call.command, event.folder)
        agent = agent.tests_run(tested, event.time) if tested else agent
        agent = agent.worker_reused() if ToolUseCounts.is_send(call) else agent
        agent = agent.fresh_over_idle() if ToolUseCounts.is_dispatch(call) and any(worker.is_idle() for worker in self.workers.scoped()) else agent
        return agent.briefed() if ToolUseCounts.is_handover(call) and ToolUseCounts.is_complete_brief(call) else agent

    def merged(self, agent: Agent, call: ToolCall) -> Agent:
        numbers = [int(line.arguments[0]) for part in call.parts if (line := WorkerLine.parsed(part.text)) and line.verb == MERGE_VERB and line.arguments[:1] and line.arguments[0].isdigit()]
        workers = self.workers.matching(id=numbers[0]) if numbers else []
        if not workers:
            return agent.unchecked_merge()
        return agent.worker_merged(str(self.branch.place(workers[0]).resolve()), workers[0].clocked_out_at())

    def has_late_worker(self, time: float) -> bool:
        return any(worker.is_unanswered(time, ANSWER_SECONDS) for worker in self.workers.scoped())

    def has_late_task(self, time: float) -> bool:
        limit = self.settings.integer(WorkersOptions.WORKER_LIMIT)
        if limit > 0 and len(self.workers.running_workers()) >= limit:
            return False
        return any(task.updated_at is not None and time - task.updated_at.timestamp() >= ANSWER_SECONDS for task in self.tasks.open_tasks())

    def used(self, agent: Agent, call: RecordedCall, time: float) -> Agent:
        mode = str(self.settings.option(WorkersOptions.MODE))
        agent = agent.in_mode(mode).tool_used()
        agent = agent.worker_waited() if mode == "orchestrator" and self.has_late_worker(time) else agent
        agent = agent.task_waited() if mode == "orchestrator" and self.has_late_task(time) else agent
        agent = agent.code_edited() if CodeFiles.has_code(call.edited_paths) else agent
        agent = agent.file_edited() if call.edited_paths else agent
        agent = agent.subagent_dispatched() if ToolUseCounts.is_subagent_dispatch(call) else agent
        return agent.researched() if ToolUseCounts.is_research(call) else agent
