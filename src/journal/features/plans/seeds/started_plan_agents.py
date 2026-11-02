from journal.features.environment_seed import EnvironmentSeed
from journal.features.plans.support.plan_agents import PlanAgents
from journal.repositories.plans import Plans
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope


class StartedPlanAgents(EnvironmentSeed):
    """At boot, a started plan's Plan agent is relaunched when its supervisor is gone."""

    def __init__(self, agents: PlanAgents, plans: Plans, environments: Environments, scope: Scope) -> None:
        self.agents, self.plans = agents, plans
        super().__init__(environments, scope)

    def run_scoped(self) -> None:
        for plan in self.plans.running_plans():
            self.agents.recover(plan)
