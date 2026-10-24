from journal.engine.nudge import Nudge
from journal.features.tasks.support.tasks_data import TasksData
from journal.features.workers.workers_nudges import WorkersNudges


def orchestrate(tasks: TasksData) -> Nudge:
    return WorkersNudges.ORCHESTRATE.create(count=len(tasks.open_ids), tasks=tasks.open_summary)
