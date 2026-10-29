from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.role import Role
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.plans import Plans
from journal.repositories.workers import Workers


class RoleInstances:
    """Which worker already is a Role's instance for a task: with cardinality journal the one worker of the Role, with plan the one worker of the Role for the task's plan, and with many none, since each job is its own instance; a task outside every plan is its own plan."""

    def __init__(self, workers: Workers, plans: Plans) -> None:
        self.workers, self.plans = workers, plans

    def plan_of(self, task: Task) -> int:
        plans = self.plans.containing(task)
        return plans[0].row_id if plans else 0

    def existing(self, role: Role, task: Task) -> Worker | None:
        instances = self.workers.role_instances(role.id)
        if role.cardinality is Cardinality.JOURNAL:
            return next(iter(instances), None)
        plan = self.plan_of(task)
        return next((worker for worker in instances if plan and worker.plan_id == plan), None) if role.cardinality is Cardinality.PLAN else None
