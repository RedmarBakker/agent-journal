from journal.engine.nudge import Nudge
from journal.events.feature_data import FeatureData
from journal.features.tasks.tasks_part import TasksPart
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_part import WorkersPart

# the tasks the line names next, of those the orchestrator's assigner hands out in turn
LINE_TASKS = 3


def delegation_lines(data: FeatureData) -> tuple[Nudge, ...]:
    delegable = data.part(WorkersPart).delegable
    if not delegable:
        return ()
    return (WorkersNudges.ORCHESTRATE.create(count=data.part(TasksPart).open_count, tasks=", ".join(str(n) for n in delegable[:LINE_TASKS])),)
