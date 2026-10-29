from journal.features.plans.support.plan_bindings import PlanBindings
from journal.models.plan import Plan
from journal.repositories.environment_owners import EnvironmentOwners


class PlanOwners:
    """The person a plan is of: the owner of its environment, or for a hub plan, which is the whole team's, the owner of this machine's environment that drives it; nobody's when neither has an owner."""

    def __init__(self, owners: EnvironmentOwners, bindings: PlanBindings) -> None:
        self.owners, self.bindings = owners, bindings

    def number(self, plan: Plan) -> int:
        return self.owners.owner_number(plan.environment_id) or self.owners.owner_number(self.bindings.environment_id(plan))

    def name(self, plan: Plan) -> str:
        number = self.number(plan)
        return self.owners.person_name(number) if number else ""
