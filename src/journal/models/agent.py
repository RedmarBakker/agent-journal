from typing import ClassVar
from dataclasses import dataclass, field, replace

from journal.events.rows.user_paused import UserPaused
from journal.events.rows.sequence_run_started import SequenceRunStarted
from journal.events.rows.sequence_run_transferred import SequenceRunTransferred
from journal.events.rows.sequence_step_adopted import SequenceStepAdopted
from journal.events.rows.sequence_step_finished import SequenceStepFinished
from journal.events.rows.sequence_step_skipped import SequenceStepSkipped
from journal.events.rows.sequence_run_paused import SequenceRunPaused
from journal.events.rows.sequence_run_abandoned import SequenceRunAbandoned
from journal.events.rows.sequence_run_cancelled import SequenceRunCancelled
from journal.events.rows.sequence_run_cannot_finish import SequenceRunCannotFinish
from journal.support.sequence_run import SequenceRun
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
from journal.models.support.wait_use import WaitUse
from journal.events.rows.waits_missing import WaitsMissing
from journal.models.scoped import Scoped


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
    tool_uses: int = 0
    code_edits: int = 0
    edited_lines: tuple[tuple[float, int], ...] = ()
    merged_lines: tuple[tuple[float, int], ...] = ()
    committed_lines: tuple[tuple[float, int], ...] = ()
    first_reports: tuple[tuple[float, int], ...] = ()
    counted_shas: tuple[str, ...] = ()
    mode: str = ""
    inbox_position: int = 0
    role: AgentRole = AgentRole.MAIN
    queued_lines: tuple[str, ...] = ()
    work_queue: AgentLoad = AgentLoad()
    message_queue: AgentLoad = AgentLoad()
    band: PressureBand = PressureBand.NONE
    band_changed_at: float = 0.0
    measures: MeasureStates = MeasureStates()
    mode_loads: dict = field(default_factory=dict)
    unlinked_message: int = 0
    unlinked_numbers: tuple[str, ...] = ()
    model_fits: tuple[str, ...] = ()
    wait_use: WaitUse = WaitUse()

    def queued(self, lines: str) -> "Agent":
        return self.with_(queued_lines=(*self.queued_lines, lines))

    def sequence_started(self, run: SequenceRun, time: float) -> "Agent":
        return self.with_event(SequenceRunStarted(environment_id=self.environment_id, time=time, agent_session=self.session, run=run))

    def sequence_transferred(self, run: SequenceRun, time: float) -> "Agent":
        return self.with_event(SequenceRunTransferred(environment_id=self.environment_id, time=time, agent_session=self.session, run=run))

    def sequence_step_adopted(self, time: float) -> "Agent":
        return self.with_event(SequenceStepAdopted(environment_id=self.environment_id, time=time, agent_session=self.session))

    def sequence_step_finished(self, run: SequenceRun, time: float) -> "Agent":
        return self.with_event(SequenceStepFinished(environment_id=self.environment_id, time=time, agent_session=self.session, run=run))

    def sequence_step_skipped(self, run: SequenceRun, time: float) -> "Agent":
        return self.with_event(SequenceStepSkipped(environment_id=self.environment_id, time=time, agent_session=self.session, run=run))

    def sequence_paused(self, reason: str, time: float) -> "Agent":
        return self.with_event(SequenceRunPaused(environment_id=self.environment_id, time=time, agent_session=self.session, reason=reason))

    def sequence_abandoned(self, reason: str, time: float) -> "Agent":
        return self.with_event(SequenceRunAbandoned(environment_id=self.environment_id, time=time, agent_session=self.session, reason=reason))

    def sequence_cancelled(self, run: SequenceRun, time: float) -> "Agent":
        return self.with_event(SequenceRunCancelled(environment_id=self.environment_id, time=time, agent_session=self.session, run=run))

    def sequence_cannot_finish(self, sequence_id: int, reason: str, time: float) -> "Agent":
        return self.with_event(SequenceRunCannotFinish(environment_id=self.environment_id, time=time, agent_session=self.session, sequence_id=sequence_id, reason=reason))

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
        return self.with_(code_edits=self.code_edits + 1)

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

    def merge_count(self, moment: float, seconds: float) -> int:
        return TimeSeries.count(self.merged_lines, moment, seconds)

    def first_report_count(self, moment: float, seconds: float) -> int:
        return TimeSeries.count(self.first_reports, moment, seconds)

    def in_mode(self, mode: str) -> "Agent":
        if self.mode == mode:
            return self
        loads = dict(self.mode_loads)
        if self.mode:
            loads[self.mode] = self.work_queue.published()
        return self.with_(mode=mode, work_queue=AgentLoad.parsed(loads[mode]) if mode in loads else AgentLoad(), mode_loads=loads)

    def model_fit_kept(self, worker: int, fit: str) -> "Agent":
        kept = tuple(entry for entry in self.model_fits if entry.split(":", 1)[0] != str(worker))
        return self.with_(model_fits=(*kept, f"{worker}:{fit}")[-MODEL_FITS_KEPT:])

    def waits_measured(self, use: WaitUse, time: float) -> "Agent":
        found = tuple(pair for pair in use.missing if pair not in self.wait_use.missing)
        measured = self.with_(wait_use=use)
        return measured.with_event(WaitsMissing(environment_id=self.environment_id, time=time, agent_session=self.session, pairs=found)) if found else measured

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

    def compacted(self) -> "Agent":
        return self.with_(tool_uses=0, inbox_position=0)

    def message_arrived(self) -> "Agent":
        return self.with_(inbox_position=self.tool_uses)

    def has_program(self) -> bool:
        return bool(self.provider)
