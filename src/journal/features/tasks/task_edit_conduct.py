from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.task_edited import TaskEdited
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_part import TasksPart


class TaskEditConduct(Conduct):
    """Every agent's conduct, the main agent's and a worker's alike: a task the agent holds whose title or brief was written anew is named to it to read again."""

    def on_task_edited(self, event: TaskEdited, settings: Settings) -> Transition:
        if event.task_id not in event.data.part(TasksPart).agent_tasks:
            return self.none()
        if event.points:
            return self.none(TasksNudges.TASK_POINTS_CHANGED.create(n=event.task_id, points=", ".join(map(str, event.points))))
        return self.none(TasksNudges.TASK_CHANGED.create(n=event.task_id))
