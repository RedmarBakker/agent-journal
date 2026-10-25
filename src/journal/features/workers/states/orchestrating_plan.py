from dataclasses import dataclass

from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.states.delegation import Delegation
from journal.features.workers.support.orchestration import orchestrate


@dataclass(frozen=True)
class OrchestratingPlan(Delegation, FollowingPlan):
    """Following a plan as the orchestrator: the task in hand is handed to a worker and its report reviewed, never done by the agent itself; with no task in hand and no checkpoint a stop is refused with the plan's open tasks to dispatch, and passes when none is open."""

    name = "orchestrating_plan"
    title = "Orchestrating a plan"

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        if self.task_id or self.checkpoint_pause:
            return super().on_stop(event, settings)
        tasks = event.data.part(TasksPart)
        return self.refuse(orchestrate(tasks)) if tasks.open_ids else self.none()
