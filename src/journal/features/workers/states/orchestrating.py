from dataclasses import dataclass

from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.feature_data import FeatureData
from journal.events.rows.worker_reported import WorkerReported
from journal.features.plans.states.plans_ready import PlansReady
from journal.features.tasks.support.tasks_data import TasksData
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.states.delegating import Delegating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.support.orchestration import orchestrate
from journal.features.workers.workers_nudges import WorkersNudges


@dataclass(frozen=True)
class Orchestrating(PlansReady):
    """The orchestrator's mode state: it plans, gives the work to workers and reviews what comes back. A stop or a long idle time with open tasks is answered with the plans to check and the workers to dispatch, a worker's report with the same, and the task and plan states it pushes say delegate where the builder's say continue."""

    name = "orchestrating"
    assigner = NoTaskAssigner
    title = "Orchestrating"

    def mode_lines(self) -> tuple[Nudge, ...]:
            return (WorkersNudges.ORCHESTRATOR_MODE.create(),)

    def plan_state(self, **fields) -> BaseState:
        return OrchestratingPlan(**fields)

    def working_state(self, **fields) -> BaseState:
        return Delegating(**fields)

    def open_lines(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        tasks = data.part(TasksPart)
        return (orchestrate(tasks),) if tasks.open_ids else ()

    def silent_nudges(self, tasks: TasksData) -> tuple[Nudge, ...]:
        return (*open_lines(tasks), *blocked_check(tasks))

    def on_worker_reported(self, event: WorkerReported, settings: Settings) -> Transition:
        return self.none(*self.silent_nudges(event.data.part(TasksPart)))


def blocked_check(tasks: TasksData) -> tuple[Nudge, ...]:
    queue = tuple(n for n in (*tasks.paused, *tasks.blocked) if n not in tasks.person_waits)
    return (WorkersNudges.BLOCKED_CHECK.create(count=len(queue), tasks=numbers(queue)),) if queue else ()


def open_lines(tasks: TasksData) -> tuple[Nudge, ...]:
    return (orchestrate(tasks),) if tasks.open_ids else ()


def numbers(ids: tuple[int, ...]) -> str:
    return ", ".join(str(n) for n in ids)
