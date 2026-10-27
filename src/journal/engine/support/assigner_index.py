from journal.engine.no_task_assigner import NoTaskAssigner
from journal.engine.task_assigner import TaskAssigner


class AssignerIndex:
    """The task assigners the features declare, one built of each class at boot, found by the class a state names."""

    def __init__(self) -> None:
        self.assigners: dict[type, TaskAssigner] = {NoTaskAssigner: NoTaskAssigner()}

    def register(self, assigner: TaskAssigner) -> None:
        self.assigners[type(assigner)] = assigner

    def instance(self, type_name: type) -> TaskAssigner:
        return self.assigners[type_name]
