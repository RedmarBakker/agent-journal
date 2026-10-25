import time
from dataclasses import asdict

from journal.engine.support.stack_history import StackHistory
from journal.engine.states.wait import Wait
from journal.engine.states_catalogue import StatesCatalogue
from journal.features.sequences.listeners.record_run_changes import RUN
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.shell_record import PART_END, PART_START
from journal.features.shell.support.activity_label import LONG_RUNS
from journal.features.tasks.states.working import Working
from journal.support.chain import Chain
from journal.config import Config
from journal.features.faults.feature import Faults
from journal.features.faults.faults_options import FaultsOptions
from journal.features.faults.support.developer_numbers import DeveloperNumbers
from journal.repositories.setting_rows import SettingRows
from journal.features.registry import Registry
from journal.providers.providers import Providers
from journal.http.agents.current_work import CurrentWork
from journal.http.agents.current_sequence import CurrentSequence
from journal.http.files.project_files import ProjectFiles
from journal.http.support.model_fields import ModelFields
from journal.models.agent import Agent
from journal.support.sequence_run import SequenceRun
from journal.repositories.entries import Entries
from journal.repositories.scheduled_jobs import ScheduledJobs
from journal.repositories.messages import Messages
from journal.support.agent_message import AgentMessage
from journal.support.file_edit import FileEdit
from journal.support.file_read import FileRead
from journal.support.file_write import FileWrite
from journal.support.recorded_call import RecordedCall
from journal.support.undecoded_tool import UndecodedTool
from journal.support.skill_load import SkillLoad
from journal.support.subagent_dispatch import SubagentDispatch
from journal.support.user_question import UserQuestion
from journal.support.command_text import CommandText
from journal.features.thinking.support.thinking_window import WORKING_STATES
from journal.features.workers.support.fitness_point import FitnessPoint
from journal.features.workers.support.fitness_scoring import FitnessScoring

STATUS = {"Stop": "idle", "SessionStarted": "idle", "SessionEnded": "stopped", "Compacting": "compacting", "PromptSubmitted": "busy", "ToolStarting": "busy", "ToolFinished": "busy", "ToolFailed": "busy", "SubagentStarted": "busy", "SubagentEnded": "busy"}
HISTORY_ENTRIES = 5
TOOL_KINDS = ("ToolStarting", "ToolFinished")
OPERATION_VERBS = {FileRead.kind: "reading a file", FileEdit.kind: "editing files", FileWrite.kind: "writing a file", SubagentDispatch.kind: "waiting for a subagent", SkillLoad.kind: "reading a skill", AgentMessage.kind: "messaging an agent", UserQuestion.kind: "asking you"}
ENDED = "ended"
# how far back the fitness timeline reaches, and the most points it reads
TIMELINE_HOURS = 6
TIMELINE_POINTS = 200


class AgentActivity:
    """An agent with what it is doing, read from the newest few entries of its own session: its status from its latest hook, the current tool or shell part, its latest thought, what it waits for, its model and context, and the sequence it runs."""

    def __init__(self, entries: Entries, states: StatesCatalogue, config: Config, providers: Providers, files: ProjectFiles, messages: Messages, current: CurrentWork, jobs: ScheduledJobs, numbers: DeveloperNumbers, registry: Registry, settings: SettingRows, scoring: FitnessScoring) -> None:
        self.entries, self.states, self.config, self.providers, self.files, self.messages, self.current = entries, states, config, providers, files, messages, current
        self.jobs, self.numbers, self.registry, self.settings, self.scoring = jobs, numbers, registry, settings, scoring

    def page(self, agents: list[Agent]) -> list[dict]:
        return [self.row(item, [] if item.state == ENDED else self.session_entries(item.session)) for item in agents]

    def session_entries(self, session: str) -> list:
        newest = [*self.entries.agent_kinds_newest(session, list(STATUS), 1), *self.entries.agent_kinds_newest(session, [*TOOL_KINDS, PART_START, PART_END], 1),
                  *self.entries.agent_kinds_newest(session, [PART_START, PART_END], 1), *self.entries.agent_kinds_newest(session, ["TurnDisplayed"], 1),
                  *self.entries.session_kind_newest(session, StackHistory.KIND, HISTORY_ENTRIES), *self.entries.session_kind_newest(session, RUN, HISTORY_ENTRIES)]
        return sorted({entry.id: entry for entry in newest}.values(), key=lambda entry: entry.id)

    def work(self, entry, entries) -> str:
        call = entry.recorded_call()
        unended = self.unended_part(entries)
        labels = [unended.data.get("doing", "")] if unended else [ActivityLabel.build(part.text) for part in call.parts[:1]]
        return next((label for label in labels if label in LONG_RUNS), call.work)

    def row(self, agent: Agent, entries) -> dict:
        hooks = [e for e in entries if e.kind not in ("nudge", "created", "updated", "deleted")]
        moves = [e for e in hooks if e.kind in STATUS]
        last = moves[-1] if moves else None
        kind = last.kind if last else ""
        state = self.states.restored(agent.state, agent.data)
        waiting_state, enabled = self.current.wait_text(agent)
        provider = self.providers.lookup(agent.provider)
        status = provider.status(agent.session, self.config.status_home)
        return {
            **ModelFields.build(agent),
            "status": "stopped" if agent.state == ENDED else self.status(agent.state, STATUS.get(kind, "idle")),
            "heard_at": last.created_at if last else agent.updated_at,
            "tool": last.data.get("tool_name", "") if last and kind in TOOL_KINDS else "",
            "tool_work": self.work(last, entries) if last and kind in TOOL_KINDS else "",
            "tool_running": kind == "ToolStarting" or self.unended_part(entries) is not None,
            "part_started_at": self.part_start(entries),
            "awaiting": waiting_state, "wait_refs": enabled, "awaiting_since": agent.updated_at if waiting_state else None,
            "model": status.model, "effort": status.effort, "usage": [asdict(window) for window in status.windows], "capabilities": sorted(provider.capabilities),
            "branch": self.files.branch(), "context": round(status.context * 100) if status.context is not None else None,
            "question_id": agent.data.get("question_id", 0) if agent.state == "waiting" else 0,
            "doing": self.activity(state, [e for e in entries if e.kind in (*TOOL_KINDS, PART_START, PART_END)]),
            "thinking": self.thinking(agent.session, hooks) if agent.state != ENDED else "",
            "thinking_at": agent.thinking_at if agent.state != ENDED else 0.0,
            "last_message": next((e.data.get("delta", "") for e in reversed(hooks) if e.kind == "TurnDisplayed"), ""),
            "stuck": agent.data.get("why", "") if agent.state == "stuck" else "",
            "sequence": self.sequence(agent),
            "stack": self.stack(agent),
            "trail": [self.trail_entry(e) for e in [e for e in entries if e.kind == StackHistory.KIND][-HISTORY_ENTRIES:]],
            "sequence_history": [{"time": e.created_at, "text": f"Sequence {e.data['n']}, {e.data['title']}: {e.data['what']}"} for e in reversed([e for e in entries if e.kind == RUN])][:HISTORY_ENTRIES],
            "jobs": self.scheduled(agent),
            "fitness": self.fitness(agent),
            "load": self.load(agent),
            **self.rolling(),
        }

    @staticmethod
    def load(agent: Agent) -> dict | None:
        load = agent.load
        if not load.is_measured():
            return None
        return {"rho": load.rho, "arrivals": load.arrivals, "clearings": load.clearings, "waiting": load.waiting, "wait_minutes": load.wait_minutes, "little": load.little,
                "waiting_refs": list(load.waiting_refs), "over_minutes": load.over_minutes}

    def fitness(self, agent: Agent) -> dict | None:
        fitness = self.scoring.scored(agent)
        if fitness is None:
            return None
        return {"mode": fitness.mode, "score": fitness.score, "is_measured": fitness.is_measured, "lines": list(fitness.lines), "timeline": self.timeline(agent.session), "timeline_hours": TIMELINE_HOURS}

    def timeline(self, session: str) -> list[dict]:
        since = time.time() - TIMELINE_HOURS * 3600
        points = [FitnessPoint.parsed(entry.data) for entry in reversed(self.entries.session_kind_newest(session, FitnessPoint.KIND, TIMELINE_POINTS))]
        return [point.shown() for point in points if point.at >= since]

    def rolling(self) -> dict:
        if not self.registry.is_enabled(Faults):
            return {}
        averages = {"hook_average_ms": self.numbers.rolling_hook_ms(), "request_average_ms": self.numbers.rolling_request_ms(),
                 "hook_parts": self.numbers.rolling_hook_parts(), "request_parts": self.numbers.rolling_request_parts()}
        if not self.settings.option(FaultsOptions.LOADS):
            return averages
        return {**averages, "points_average": self.numbers.rolling_points(), "point_parts": self.numbers.rolling_point_parts()}

    def scheduled(self, agent: Agent) -> list[dict]:
        moment = time.time()
        return [{"id": job.job_id, "cron": job.cron, "prompt": job.prompt, "recurring": job.recurring, "created_at": job.created_at} for job in self.jobs.session_jobs(agent.session) if job.is_running(moment)] if agent.state != ENDED else []

    @staticmethod
    def status(state: str, reported: str) -> str:
        return "working" if state in WORKING_STATES and reported == "busy" else reported

    def thinking(self, session: str, hooks) -> str:
        thoughts = self.messages.thoughts(session, 1)
        if not thoughts:
            return ""
        saved = [e.created_at for e in hooks if e.kind == "TurnDisplayed"]
        later = [time for time in (saved[-1] if saved else None, self.entries.last_prompt(session)) if time is not None]
        return "" if any(time > thoughts[-1].creation_time for time in later) else thoughts[-1].text

    @staticmethod
    def sequence(agent: Agent) -> CurrentSequence | None:
        runs = [SequenceRun.build(raw) for raw in agent.sequence_runs or ()]
        if not runs:
            return None
        run = runs[-1]
        return CurrentSequence(sequence_id=run.sequence_id, title=run.title, step=run.step + 1, steps=len(run.steps), text=run.text, blocks=run.blocks, subject=run.subject, waiting_runs=len(runs) - 1)

    def activity(self, state, hooks) -> str:
        last = hooks[-1] if hooks else None
        if last and last.kind in (PART_START, PART_END):
            return CommandText.shown(last.data["part"])
        if last and last.kind == "ToolStarting":
            return self.tool_activity(last.recorded_call())
        part = self.unended_part(hooks)
        if part is not None:
            return CommandText.shown(part.data["part"])
        return self.described(state) or ("at work" if hooks else "")

    def part_start(self, entries) -> float | None:
        part = self.unended_part(entries)
        return part.data["time"] if part is not None else None

    @staticmethod
    def unended_part(entries):
        parts = [e for e in entries if e.kind in (PART_START, PART_END)]
        return parts[-1] if parts and parts[-1].kind == PART_START else None

    @staticmethod
    def tool_activity(call: RecordedCall) -> str:
        if call.parts:
            return call.parts[0].text
        if isinstance(call.operation, UndecodedTool):
            return f"using {call.operation.name}"
        return OPERATION_VERBS.get(call.operation.kind, "working")

    def described(self, state) -> str:
        if isinstance(state, Wait):
            return state.wait_description()[0]
        return state.focus if isinstance(state, Working) else ""

    def stack(self, agent: Agent) -> list[dict]:
        shown = []
        for state in reversed(self.states.stack(agent).states):
            awaits = state.wait_description()[0] if isinstance(state, Wait) else ""
            shown.append({"name": state.name, "title": self.states.title(state.name), "values": state.serialized(), "awaits": awaits})
        return shown

    @staticmethod
    def trail_entry(entry) -> dict:
        return {"time": entry.created_at, "before": [row["state"] for row in entry.data.get("before", [])], "after": [row["state"] for row in entry.data.get("after", [])], "cause": entry.data.get("cause", ""), "refused": entry.data.get("refused", ""), "line": entry.data.get("line", "")}
