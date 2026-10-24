from dataclasses import dataclass, replace

from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.features.plans.states.plan_work import PlanWork
from journal.features.workers.support.orchestration import orchestrate
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.workers_nudges import WorkersNudges


@dataclass(frozen=True)
class Delegation(PlanWork):
    """Current work as the orchestrator, a task or a plan's: instructed to give it to a worker and review the report, and at a stop with tasks open instructed to orchestrate them."""

    def continue_nudge(self, time: float) -> Nudge:
        return WorkersNudges.TASK_DELEGATION.create(name=self.label(), logged=self.logged_words(time))

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        answer = super().on_stop(event, settings)
        tasks = event.data.part(TasksPart)
        return replace(answer, nudges=(*answer.nudges, orchestrate(tasks))) if tasks.open_ids else answer
