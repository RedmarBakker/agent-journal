from dataclasses import dataclass, replace

from journal.engine.nudge import Nudge
from journal.engine.support.block import Block
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.plan_abandoned import PlanAbandoned
from journal.events.rows.plan_finished import PlanFinished
from journal.events.rows.plan_postponed import PlanPostponed
from journal.events.rows.plan_started import PlanStarted
from journal.events.rows.task_closed import TaskClosed
from journal.events.rows.task_started import TaskStarted
from journal.events.feature_data import FeatureData
from journal.features.plans.states.plan_work import PlanWork
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.plans.plans_part import PlansPart
from journal.features.tasks.tasks_part import TasksPart


@dataclass(frozen=True)
class FollowingPlan(PlanWork):
    """Working with a current plan, for the plan's whole life. A finished task starts the next: the plans feature writes it and the state keeps the top as that task; a task started outside the plan is the current task all the same, since only one task is current at a time. At a checkpoint the state has no current task: the stop waits for the user, or in auto mode is refused and the agent instructed to continue; at a phase end whose testing template's commands have not passed since its last task, the stop is refused with those commands to run, and at one that is no checkpoint, once they pass, the agent is instructed to begin the next phase; a checkpoint keeps its own line. Popped when the plan is done, postponed or abandoned, and on resume when the plan is no longer the one started here."""

    name = "following_plan"
    title = "Following a plan"
    plan_id: int = 0
    approved: bool = False
    origin_state: int = 0
    checkpoint_pause: bool = False
    phase: int = 0
    phase_held: bool = False

    def on_plan_started(self, event: PlanStarted, settings: Settings) -> Transition:
        return self.none()

    def label(self) -> str:
        return super().label() if self.task_id else f"plan {self.plan_id}, with no task in hand"

    def on_push(self, settings: Settings) -> tuple[Nudge, ...] | Block:
        return () if self.approved else Block(PlansNudges.UNAPPROVED_PLAN.create(n=self.plan_id))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if not self.checkpoint_pause:
            return super().on_stop(event, settings)
        if event.prior_refusal:
            return self.none()
        started = event.data.part(PlansPart).started
        if started is not None and started.phase_commands:
            return self.refuse(PlansNudges.PHASE_END_TESTS.create(n=self.plan_id, phase=self.phase, commands=" and ".join(started.phase_commands)))
        if settings.value(TasksOptions.AUTO) or self.phase_held:
            return self.refuse(PlansNudges.PHASE_END.create(n=self.plan_id, phase=self.phase))
        return self.none(PlansNudges.CHECKPOINT_PHASE_END.create(n=self.plan_id, phase=self.phase))

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        if self.checkpoint_pause:
            started = event.data.part(PlansPart).started
            commands = started.phase_commands if started is not None else ()
            return self.none(PlansNudges.PHASE_END_TESTS.create(n=self.plan_id, phase=self.phase, commands=" and ".join(commands)) if commands else PlansNudges.CHECKPOINT_PHASE_END.create(n=self.plan_id, phase=self.phase))
        return super().on_session_started(event, settings)

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.none() if self.checkpoint_pause else super().on_tool_starting(event, settings)

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        if event.task_id not in event.data.part(TasksPart).agent_tasks:
            return self.none()
        return self.swap(replace(self, task_id=event.task_id, checkpoint_pause=False, phase=0, phase_held=False, logged_at=event.time, edits=0))

    def on_task_closed(self, event: TaskClosed, settings: Settings) -> Transition:
        if event.task_id != self.task_id:
            return self.none()
        started = event.data.part(PlansPart).started
        if started is not None and started.checkpoint_pause:
            return self.swap(replace(self, task_id=0, origin_state=event.task_id, checkpoint_pause=True, phase=started.checkpoint_phase, phase_held=bool(started.phase_commands) and not started.is_checkpoint))
        return self.swap(replace(self, task_id=0, origin_state=event.task_id))

    def on_plan_finished(self, event: PlanFinished, settings: Settings) -> Transition:
        return self.pop(PlansNudges.PLAN_FINISHED.create(n=event.plan_id)) if event.plan_id == self.plan_id else self.none()

    def on_plan_postponed(self, event: PlanPostponed, settings: Settings) -> Transition:
        if event.plan_id != self.plan_id:
            return self.none()
        return self.pop(PlansNudges.PLAN_POSTPONED.create(n=event.plan_id)) if event.user_origin else self.pop()

    def on_plan_abandoned(self, event: PlanAbandoned, settings: Settings) -> Transition:
        if event.plan_id != self.plan_id:
            return self.none()
        return self.pop(PlansNudges.PLAN_ABANDONED.create(n=event.plan_id)) if event.user_origin else self.pop()

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        started = data.part(PlansPart).started
        if started is None or started.plan_id != self.plan_id:
            return self.pop()
        if started.started_task and started.started_task != self.task_id:
            return self.swap(replace(self, task_id=started.started_task, checkpoint_pause=False, phase=0, edits=0))
        return super().on_resume(data, settings)
