from dataclasses import dataclass, replace

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.plans_ready import PlansReady


@dataclass(frozen=True)
class LeadingPlan(PlansReady):
    """The floor of a Plan agent, in its plan's own environment: a session start names its plan before the plan's state is pushed."""

    name = "leading_plan"
    title = "Leading a plan"

    plan_id: int = 0

    @classmethod
    def keeps_floor(cls) -> bool:
        return True

    def reset_states(self, _states) -> tuple["LeadingPlan", ...]:
        return (self.restored({"plan_id": self.plan_id}),)

    def subject(self) -> str:
        return f"plan {self.plan_id}"

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        answer = super().on_session_started(event, settings)
        return replace(answer, nudges=(PlansNudges.LEADING_PLAN.create(n=self.plan_id), *answer.nudges))
