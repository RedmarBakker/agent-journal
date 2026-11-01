from typing import ClassVar
from dataclasses import dataclass, field, replace

from journal.support.timeout import Timeout
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
from journal.events.rows.plan_agent_stopped import PlanAgentStopped
from journal.events.rows.launch_takeover import LaunchTakeover
from journal.events.rows.overview_read import OverviewRead
from journal.events.rows.context_decided import ContextDecided
from journal.events.rows.skill_read import SkillRead
from journal.events.rows.places_scaled import PlacesScaled
from journal.support.agent_role import AgentRole
from journal.models.support.agent_load import AgentLoad
from journal.models.scoped import Scoped


# the state an agent's row is in once its session has ended
ENDED_STATE = "ended"

@dataclass(frozen=True)

class Agent(Scoped):
    unshown_fields: ClassVar[tuple[str, ...]] = ("work_queue", "message_queue")


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
    inbox_position: int = 0
    role: AgentRole = AgentRole.MAIN
    queued_lines: tuple[str, ...] = ()
    work_queue: AgentLoad = AgentLoad()
    message_queue: AgentLoad = AgentLoad()
    previous_sessions: tuple[str, ...] = ()
    previous_session_updated_at: float = 0.0

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

    def is_top_state(self, state_name: str) -> bool:
        return bool(self.stack) and self.stack[-1].get("state") == state_name

    def is_thinking(self) -> bool:
        return self.thinking_at > 0

    def user_resumed(self, time: float) -> "Agent":
        return self.with_event(UserResumed(environment_id=self.environment_id, time=time, agent_session=self.session))

    def with_session(self, session: str, provider: str) -> "Agent":
        kept = tuple(entry for entry in self.previous_sessions if entry.partition(":")[2] not in (session, self.session))
        earlier = (f"{self.provider}:{self.session}",) if self.session else ()
        updated_at = self.updated_at.timestamp() if self.updated_at else 0.0
        return self.with_(session=session, provider=provider, previous_sessions=(*kept, *earlier), previous_session_updated_at=updated_at)

    def last_sessions(self) -> dict[str, str]:
        sessions = dict(entry.split(":", 1) for entry in self.previous_sessions)
        return {**sessions, self.provider: self.session}

    def retired(self, time: float) -> "Agent":
        return self.with_event(SessionRetired(environment_id=self.environment_id, time=time, session=self.session, agent_session=self.session))

    def plan_stopped(self, plan_id: int, time: float) -> "Agent":
        return self.with_event(PlanAgentStopped(environment_id=self.environment_id, time=time, session=self.session, plan_id=plan_id))

    def upgraded(self, previous: str, version: str, time: float) -> "Agent":
        return self.with_event(LaunchTakeover(environment_id=self.environment_id, time=time, agent_session=self.session, previous=previous, version=version))

    def overview_read(self, time: float) -> "Agent":
        return self.with_(is_overview_read=True).with_event(OverviewRead(environment_id=self.environment_id, time=time))

    def context_decided(self, time: float) -> "Agent":
        return self.with_(threshold_due=0).with_event(ContextDecided(environment_id=self.environment_id, time=time, threshold=self.threshold_due, agent_session=self.session))

    def skill_read(self, name: str, digest: str, time: float) -> "Agent":
        loaded = {**self.skills_loaded, name: digest}
        obligations = tuple(skill for skill in self.skills_due if skill != name)
        return self.with_(skills_loaded=loaded, skills_due=obligations).with_event(SkillRead(environment_id=self.environment_id, time=time, skill=name))

    def tool_used(self) -> "Agent":
        return self.with_(tool_uses=self.tool_uses + 1)

    def code_edited(self) -> "Agent":
        return self.with_(code_edits=self.code_edits + 1)

    def queue_loads_measured(self, work_queue: AgentLoad, message_queue: AgentLoad) -> "Agent":
        return self.with_(work_queue=replace(work_queue, scaled_at=self.work_queue.scaled_at), message_queue=message_queue)

    def place_opened(self, places: int, time: float) -> "Agent":
        return self.places_scaled(places, time, self.work_queue.busy_minutes, True)

    def place_closed(self, places: int, time: float) -> "Agent":
        return self.places_scaled(places, time, self.work_queue.low_minutes, False)

    def places_scaled(self, places: int, time: float, minutes: float, opened: bool) -> "Agent":
        event = PlacesScaled(environment_id=self.environment_id, time=time, agent_session=self.session, places=places, rho=self.work_queue.rho, minutes=minutes, opened=opened)
        return self.with_(work_queue=self.work_queue.scaled(time)).with_event(event)

    def compacted(self) -> "Agent":
        return self.with_(tool_uses=0, inbox_position=0)

    def message_arrived(self) -> "Agent":
        return self.with_(inbox_position=self.tool_uses)

    def has_program(self) -> bool:
        return bool(self.provider)

    def is_main(self) -> bool:
        return self.role == AgentRole.MAIN
