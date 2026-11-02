from journal.features.plans.support.plan_agents import PlanAgents
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from tests.stories.fixtures.main.organization_plan_with_stale_owner_row import OrganizationPlanWithStaleOwnerRow


class OrganizationPlanWithStaleAgentLink(OrganizationPlanWithStaleOwnerRow):
    """A fresh Plan agent was prepared after an older link to an ended owner-environment row."""

    parent = OrganizationPlanWithStaleOwnerRow

    def steps(self, story) -> None:
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        environment = story.app.container.get(Environments).existing(f"plan-{plan.id}")
        fresh = story.app.container.get(PlanAgents).prepared(plan, environment, plan.environment_id, Actor.system())
        with story.app.container.get(Scope).environment(environment.row_id):
            story.app.container.get(Agents).save(fresh.with_(is_overview_read=False), Actor.system())
        story.observed("a fresh preparation replaces the stale Plan-agent link", None, None)
