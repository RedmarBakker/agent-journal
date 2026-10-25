from journal.engine.demand import Demand
from journal.events.feature_data import FeatureData
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_part import TasksPart
from journal.support.timeout import Timeout


def blocking_priorities(data: FeatureData) -> tuple[int, ...] | None:
    return data.part(TasksPart).blocking_priorities or None


def task_numbers(tasks: tuple[int, ...]) -> str:
    return ", ".join(str(task) for task in tasks)


class TasksDemands:
    """What the tasks feature demands of the agent: once enough open tasks it made sit at the default priority, each is given its priority or all are confirmed before its next write."""

    PRIORITIES = Demand(
        key="tasks.priorities",
        requirement=blocking_priorities,
        line=lambda tasks, balance: TasksNudges.PRIORITIES_REFUSAL.create(count=len(tasks), tasks=task_numbers(tasks)),
        refusal=lambda tasks: TasksNudges.PRIORITIES_REFUSAL.create(count=len(tasks), tasks=task_numbers(tasks)),
        exemption=lambda event, tasks: False,
        span=lambda settings: Timeout.tool_uses(0),
        block_scope=lambda event: bool(event.call.writes),
    )
