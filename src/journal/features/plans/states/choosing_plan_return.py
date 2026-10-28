from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.plan_return_answer import PlanReturnAnswer
from journal.features.plans.plans_nudges import PlansNudges


@dataclass(frozen=True)
class ChoosingPlanReturn(BaseState):
    """The agent paused its plan itself and took up a task outside it: until it says whether it returns to the plan once that task is done, every tool but a journal command and every stop waits, and its answer pops this state."""

    name = "choosing_plan_return"
    title = "Choosing whether to return to the plan"
    plan_id: int = 0
    task_id: int = 0

    def takes_pushes(self) -> bool:
        return False

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.none() if event.call.is_journal else self.refuse(self.question())

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.refuse(self.question())

    def on_plan_return_answer(self, event: PlanReturnAnswer, settings: Settings) -> Transition:
        return self.pop() if event.plan_id == self.plan_id else self.none()

    def question(self):
        return PlansNudges.PLAN_RETURN_QUESTION.create(n=self.plan_id, task=self.task_id)
