from typing import ClassVar
from dataclasses import asdict, dataclass, field, replace

from journal.events.rows.user_paused import UserPaused
from journal.events.rows.agent_thinking import AgentThinking
from journal.events.rows.agent_thinking_ended import AgentThinkingEnded
from journal.events.rows.user_resumed import UserResumed
from journal.events.rows.session_retired import SessionRetired
from journal.events.rows.launch_takeover import LaunchTakeover
from journal.events.rows.overview_read import OverviewRead
from journal.events.rows.context_decided import ContextDecided
from journal.events.rows.skill_read import SkillRead
from journal.events.rows.places_scaled import PlacesScaled
from journal.support.agent_role import AgentRole
from journal.models.support.agent_load import AgentLoad
from journal.models.support.time_series import SHA_COUNT, TimeSeries
from journal.models.support.measure_states import MeasureStates
from journal.models.support.pressure_band import PressureBand
from journal.events.rows.quick_report_dropped import QuickReportDropped
from journal.events.rows.tiny_job_dropped import TinyJobDropped
from journal.models.support.queue_use import QueueUse
from journal.models.support.report_use import ReportUse
from journal.models.support.wait_use import WaitUse
from journal.events.rows.waits_missing import WaitsMissing
from journal.models.scoped import Scoped


# how many of its newest tool uses an agent's subagent dispatches, research, handovers and file edits are counted over
WORK_WINDOW_USES = 50
WINDOWED_USES = ("subagent_dispatch_uses", "research_uses", "handover_uses", "file_edit_uses", "merge_uses", "prepared_merge_uses", "reuse_uses", "fresh_idle_uses", "briefed_uses", "late_worker_uses", "late_task_uses", "task_filed_uses", "task_completed_uses")
# how many of the newest merged jobs it handed out an agent's model fit is counted over
MODEL_FITS_KEPT = 10

@dataclass(frozen=True)

class Agent(Scoped):
    shared: ClassVar[bool] = False
    unshown_fields: ClassVar[tuple[str, ...]] = ("work_queue", "message_queue", "mode_loads", "band_changed_at", "measures")


    session: str = ""
    provider: str = ""
    state: str = "idle"
    data: dict = field(default_factory=dict)
    thinking_at: float = 0.0
    stack: tuple = ()
    skills_loaded: dict = field(default_factory=dict)
    context_threshold: int = 0
    is_overview_read: bool = True
    threshold_due: int = 0
    skills_due: tuple[str, ...] = ()
    sequence_runs: tuple = ()
    tool_uses: int = 0
    code_edits: int = 0
    consecutive_handovers: int = 0
    last_handover_at: float = 0.0
    subagent_dispatch_uses: tuple[int, ...] = ()
    research_uses: tuple[int, ...] = ()
    handover_uses: tuple[int, ...] = ()
    file_edit_uses: tuple[int, ...] = ()
    merge_uses: tuple[int, ...] = ()
    prepared_merge_uses: tuple[int, ...] = ()
    edited_lines: tuple[tuple[float, int], ...] = ()
    merged_lines: tuple[tuple[float, int], ...] = ()
    committed_lines: tuple[tuple[float, int], ...] = ()
    first_reports: tuple[tuple[float, int], ...] = ()
    counted_shas: tuple[str, ...] = ()
    task_filed_uses: tuple[int, ...] = ()
    task_completed_uses: tuple[int, ...] = ()
    reuse_uses: tuple[int, ...] = ()
    fresh_idle_uses: tuple[int, ...] = ()
    briefed_uses: tuple[int, ...] = ()
    late_worker_uses: tuple[int, ...] = ()
    late_task_uses: tuple[int, ...] = ()
    is_proof_read: bool = False
    test_run_at: float = 0.0
    test_run_folder: str = ""
    mode: str = ""
    mode_started_use: int = 0
    inbox_position: int = 0
    role: AgentRole = AgentRole.MAIN
    queued_lines: tuple[str, ...] = ()
    work_queue: AgentLoad = AgentLoad()
    message_queue: AgentLoad = AgentLoad()
    band: PressureBand = PressureBand.NONE
    band_changed_at: float = 0.0
    measures: MeasureStates = MeasureStates()
    mode_loads: dict = field(default_factory=dict)
    fitness_level: int = 100
    unlinked_message: int = 0
    unlinked_numbers: tuple[str, ...] = ()
    model_fits: tuple[str, ...] = ()
    wait_use: WaitUse = WaitUse()
    report_use: ReportUse = ReportUse()
    queue_use: QueueUse = QueueUse()

    def queued(self, lines: str) -> "Agent":
        return self.with_(queued_lines=(*self.queued_lines, lines))

    def user_paused(self, time: float) -> "Agent":
        return self.with_event(UserPaused(environment_id=self.environment_id, time=time, agent_session=self.session))

    def thinking_started(self, time: float) -> "Agent":
        return self.with_(thinking_at=time).with_event(AgentThinking(environment_id=self.environment_id, time=time, agent_session=self.session))

    def thinking_ended(self, time: float) -> "Agent":
        return self.with_(thinking_at=0.0).with_event(AgentThinkingEnded(environment_id=self.environment_id, time=time, agent_session=self.session))

    def is_thinking(self) -> bool:
        return self.thinking_at > 0

    def user_resumed(self, time: float) -> "Agent":
        return self.with_event(UserResumed(environment_id=self.environment_id, time=time, agent_session=self.session))

    def retired(self, time: float) -> "Agent":
        return self.with_event(SessionRetired(environment_id=self.environment_id, time=time, agent_session=self.session))

    def upgraded(self, previous: str, version: str, time: float) -> "Agent":
        return self.with_event(LaunchTakeover(environment_id=self.environment_id, time=time, agent_session=self.session, previous=previous, version=version))

    def overview_read(self, time: float) -> "Agent":
        return self.with_(is_overview_read=True).with_event(OverviewRead(environment_id=self.environment_id, time=time))

    def context_decided(self, time: float) -> "Agent":
        return self.with_(threshold_due=0).with_event(ContextDecided(environment_id=self.environment_id, time=time, threshold=self.threshold_due))

    def skill_read(self, name: str, digest: str, time: float) -> "Agent":
        loaded = {**self.skills_loaded, name: digest}
        obligations = tuple(skill for skill in self.skills_due if skill != name)
        return self.with_(skills_loaded=loaded, skills_due=obligations).with_event(SkillRead(environment_id=self.environment_id, time=time, skill=name))

    def tool_used(self) -> "Agent":
        return self.with_(tool_uses=self.tool_uses + 1)

    def code_edited(self) -> "Agent":
        return self.with_(code_edits=self.code_edits + 1, consecutive_handovers=0)

    def with_handover(self, time: float) -> "Agent":
        return self.with_(consecutive_handovers=self.consecutive_handovers + 1, last_handover_at=time, handover_uses=self.windowed((*self.handover_uses, self.tool_uses)))

    def lines_edited(self, lines: int, time: float, cutoff: float) -> "Agent":
        return self.with_(edited_lines=TimeSeries.add(self.edited_lines, (time, lines), cutoff)) if lines else self

    def lines_merged(self, lines: int, time: float, cutoff: float) -> "Agent":
        return self.with_(merged_lines=TimeSeries.add(self.merged_lines, (time, lines), cutoff)) if lines else self

    def lines_committed(self, sha: str, lines: int, time: float, cutoff: float) -> "Agent":
        shas = (*self.counted_shas, sha)[-SHA_COUNT:]
        return self.with_(committed_lines=TimeSeries.add(self.committed_lines, (time, lines), cutoff), counted_shas=shas)

    def first_reported(self, task: int, time: float, cutoff: float) -> "Agent":
        return self.with_(first_reports=TimeSeries.add(self.first_reports, (time, task), cutoff))

    def shas_counted(self, shas: tuple[str, ...]) -> "Agent":
        return self.with_(counted_shas=(*self.counted_shas, *shas)[-SHA_COUNT:]) if shas else self

    def authored_total(self, moment: float, seconds: float) -> int:
        last_commit = self.committed_lines[-1][0] if self.committed_lines else 0.0
        provisional = sum(lines for time, lines in self.edited_lines if last_commit < time and moment - seconds < time <= moment)
        return self.committed_total(moment, seconds) + provisional

    def is_sha_counted(self, sha: str) -> bool:
        return sha in self.counted_shas

    def edited_total(self, moment: float, seconds: float) -> int:
        return TimeSeries.total(self.edited_lines, moment, seconds)

    def merged_total(self, moment: float, seconds: float) -> int:
        return TimeSeries.total(self.merged_lines, moment, seconds)

    def committed_total(self, moment: float, seconds: float) -> int:
        return TimeSeries.total(self.committed_lines, moment, seconds)

    def first_report_count(self, moment: float, seconds: float) -> int:
        return TimeSeries.count(self.first_reports, moment, seconds)

    def handover_lines(self) -> int:
        return sum(lines for time, lines in self.edited_lines if time > self.last_handover_at)

    def task_filed(self) -> "Agent":
        return self.with_(task_filed_uses=self.windowed((*self.task_filed_uses, self.tool_uses)))

    def task_completed(self) -> "Agent":
        return self.with_(task_completed_uses=self.windowed((*self.task_completed_uses, self.tool_uses)))

    def file_edited(self) -> "Agent":
        return self.with_(file_edit_uses=self.windowed((*self.file_edit_uses, self.tool_uses)))

    def subagent_dispatched(self) -> "Agent":
        return self.with_(subagent_dispatch_uses=self.windowed((*self.subagent_dispatch_uses, self.tool_uses)))

    def researched(self) -> "Agent":
        return self.with_(research_uses=self.windowed((*self.research_uses, self.tool_uses)))

    def in_mode(self, mode: str) -> "Agent":
        if self.mode == mode:
            return self
        loads = dict(self.mode_loads)
        if self.mode:
            loads[self.mode] = asdict(self.work_queue)
        return self.with_(mode=mode, mode_started_use=self.tool_uses, work_queue=AgentLoad.parsed(loads[mode]) if mode in loads else AgentLoad(), mode_loads=loads)

    def worker_merged(self, place: str, clocked_out_at: float) -> "Agent":
        tested = bool(self.test_run_folder) and self.test_run_folder == place and self.test_run_at >= clocked_out_at
        prepared = (*self.prepared_merge_uses, self.tool_uses) if self.is_proof_read and tested else self.prepared_merge_uses
        return self.unchecked_merge().with_(prepared_merge_uses=self.windowed(prepared))

    def unchecked_merge(self) -> "Agent":
        return self.with_(merge_uses=self.windowed((*self.merge_uses, self.tool_uses)), is_proof_read=False, test_run_at=0.0, test_run_folder="")

    def proof_read(self) -> "Agent":
        return self.with_(is_proof_read=True)

    def tests_run(self, folder: str, time: float) -> "Agent":
        return self.with_(test_run_at=time, test_run_folder=folder)

    def worker_reused(self) -> "Agent":
        return self.with_(reuse_uses=self.windowed((*self.reuse_uses, self.tool_uses)))

    def fresh_over_idle(self) -> "Agent":
        return self.with_(fresh_idle_uses=self.windowed((*self.fresh_idle_uses, self.tool_uses)))

    def briefed(self) -> "Agent":
        return self.with_(briefed_uses=self.windowed((*self.briefed_uses, self.tool_uses)))

    def model_fit_kept(self, worker: int, fit: str) -> "Agent":
        kept = tuple(entry for entry in self.model_fits if entry.split(":", 1)[0] != str(worker))
        return self.with_(model_fits=(*kept, f"{worker}:{fit}")[-MODEL_FITS_KEPT:])

    def waits_measured(self, use: WaitUse, time: float) -> "Agent":
        found = tuple(pair for pair in use.missing if pair not in self.wait_use.missing)
        measured = self.with_(wait_use=use)
        return measured.with_event(WaitsMissing(environment_id=self.environment_id, time=time, agent_session=self.session, pairs=found)) if found else measured

    def quick_report_dropped(self, use: ReportUse, time: float, worker: int, open_tasks: int) -> "Agent":
        return self.with_(report_use=use).with_event(QuickReportDropped(environment_id=self.environment_id, time=time, agent_session=self.session, worker=worker, open_tasks=open_tasks, points=use.drop_points))

    def tiny_job_dropped(self, use: ReportUse, time: float, worker: int, seconds: int) -> "Agent":
        return self.with_(report_use=use).with_event(TinyJobDropped(environment_id=self.environment_id, time=time, agent_session=self.session, worker=worker, seconds=seconds, points=use.drop_points))

    def band_moved(self, band: PressureBand, time: float) -> "Agent":
        return self if band == self.band else self.with_(band=band, band_changed_at=time)

    def measures_worked(self, measures: MeasureStates) -> "Agent":
        return self.with_(measures=measures)

    def measure_line_sent(self, key: str, time: float) -> "Agent":
        return self.with_(measures=self.measures.line_sent(key, time))

    def queues_measured(self, work_queue: AgentLoad, message_queue: AgentLoad) -> "Agent":
        return self.with_(work_queue=replace(work_queue, scaled_at=self.work_queue.scaled_at), message_queue=message_queue)

    def place_opened(self, places: int, time: float) -> "Agent":
        return self.with_(work_queue=self.work_queue.scaled(time)).with_event(PlacesScaled(environment_id=self.environment_id, time=time, agent_session=self.session, places=places, rho=self.work_queue.rho, minutes=self.work_queue.over_minutes, opened=True))

    def place_closed(self, places: int, time: float) -> "Agent":
        return self.with_(work_queue=self.work_queue.scaled(time)).with_event(PlacesScaled(environment_id=self.environment_id, time=time, agent_session=self.session, places=places, rho=self.work_queue.rho, minutes=self.work_queue.under_minutes, opened=False))

    def worker_waited(self) -> "Agent":
        return self.with_(late_worker_uses=self.windowed((*self.late_worker_uses, self.tool_uses)))

    def task_waited(self) -> "Agent":
        return self.with_(late_task_uses=self.windowed((*self.late_task_uses, self.tool_uses)))

    def windowed(self, uses: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(use for use in uses if self.tool_uses - WORK_WINDOW_USES < use <= self.tool_uses)

    def compacted(self) -> "Agent":
        shifted = {name: tuple(use - self.tool_uses for use in getattr(self, name)) for name in WINDOWED_USES}
        return self.with_(tool_uses=0, mode_started_use=0, inbox_position=0, **shifted)

    def message_arrived(self) -> "Agent":
        return self.with_(inbox_position=self.tool_uses)

    def has_program(self) -> bool:
        return bool(self.provider)
