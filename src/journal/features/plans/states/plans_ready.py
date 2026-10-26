from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.events.feature_data import FeatureData
from journal.events.rows.plan_started import PlanStarted
from journal.events.rows.task_started import TaskStarted
from journal.features.tasks.states.ready import Ready
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_part import PlansPart
from journal.features.tasks.tasks_part import TasksPart
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.plans_working import PlansWorking
from journal.features.plans.support.plan_start_task_assigner import PlanStartTaskAssigner


@dataclass(frozen=True)
class PlansReady(Ready):
    """Idle with plans on: a task of the plan this agent owns started here, the plan's start with a task this agent owns and a session that finds one started push the plan's state, and a stop is blocked while an approved plan waits to start; its task assigner starts the oldest approved plan between the agent's own paused task and a free one; every other moment is Idle's."""

    assigner = PlanStartTaskAssigner

    def mode_lines(self) -> tuple[Nudge, ...]:
        return (PlansNudges.BUILDER_MODE.create(),)

    def plan_state(self, **fields) -> BaseState:
        return FollowingPlan(**fields)

    def approved_plan_state(self, plan_id: int, task_id: int, time: float, task_noun: str) -> BaseState:
        return self.plan_state(plan_id=plan_id, task_id=task_id, approved=True, logged_at=time, task_noun=task_noun)

    def working_state(self, **fields) -> BaseState:
        return PlansWorking(**fields)

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        started = event.data.part(PlansPart).started
        if not started:
            return super().on_session_started(event, settings)
        active = self.active(event.time)
        return active.push(active.plan_state(plan_id=started.plan_id, task_id=started.started_task, approved=True, logged_at=event.time))

    def on_task_started(self, event: TaskStarted, settings: Settings) -> Transition:
        started = event.data.part(PlansPart).started
        if started and event.task_id in started.recent_tasks and event.task_id in event.data.part(TasksPart).agent_tasks:
            return self.push(self.approved_plan_state(started.plan_id, event.task_id, event.time, self.task_noun(event.data, event.environment_id)))
        return super().on_task_started(event, settings)

    def on_plan_started(self, event: PlanStarted, settings: Settings) -> Transition:
        if event.task_id and event.task_id not in event.data.part(TasksPart).agent_tasks:
            return self.none()
        return self.push(self.approved_plan_state(event.plan_id, event.task_id, event.time, self.task_noun(event.data, event.environment_id)))

    def open_lines(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        approved = data.part(PlansPart).approved
        if approved:
            return (PlansNudges.APPROVED_UNSTARTED.create(n=approved[0]),)
        return super().open_lines(data, settings)
