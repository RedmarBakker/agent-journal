from journal.features.plans.support.plan_testing import PlanTesting
from journal.models.plan import Plan
from journal.models.task import Task
from journal.repositories.plans import Plans
from journal.support.rejection import Rejection


class PlanDelegation:
    """The work a worker is given when it is dispatched on a whole plan or on one phase of it: the plan's tasks a worker may take, in the plan's order, phase by phase, and how the plan says its work is tested."""

    def __init__(self, plans: Plans, testing: PlanTesting) -> None:
        self.plans, self.testing = plans, testing

    def tasks(self, plan_id: int, phase_number: int) -> list[Task]:
        plan = self.plans.find(plan_id)
        if not plan.state.is_startable():
            raise Rejection(f"plan {plan_id} is {plan.state.value}: only an approved plan goes to a worker")
        handed = self.plans.assignable_tasks(self.phase_task_ids(plan, phase_number))
        if not handed:
            raise Rejection(f"{self.scope_name(plan_id, phase_number)} has no open task with a brief to hand a worker")
        return handed

    def phase_task_ids(self, plan: Plan, phase_number: int) -> list[int]:
        phases = self.plans.plan_phases(plan)
        members = self.plans.phase_task_ids(phases)
        if not phase_number:
            phased = [n for phase in phases for n in members[phase.id]]
            return phased + self.plans.unphased_task_ids(plan, phased)
        if not 0 < phase_number <= len(phases):
            raise Rejection(f"plan {plan.id} has {len(phases)} phases, so it has no phase {phase_number}")
        return members[phases[phase_number - 1].id]

    def testing_brief(self, plan_id: int) -> str:
        templates = self.testing.chosen(self.plans.find(plan_id))
        return templates[0].brief if templates else ""

    @staticmethod
    def scope_name(plan_id: int, phase_number: int) -> str:
        return f"phase {phase_number} of plan {plan_id}" if phase_number else f"plan {plan_id}"
