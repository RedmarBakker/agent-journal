from journal.features.plans.support.plan_bindings import PlanBindings
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.support.ref import Ref
from journal.repositories.plans import Plans
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


class OrganizationPlanSeatWithoutBinding(OrganizationPlanWithDomainSeats):
    """A started organization plan's seat environment has no plan visibility binding."""

    parent = OrganizationPlanWithDomainSeats

    def steps(self, story) -> None:
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        story.app.container.get(PlanBindings).unbind(Ref.build(plan), Actor.system())
        agent = story.app.container.get(PlanAgents).agent(plan)
        with story.app.container.get(Scope).environment(agent.environment_id):
            story.app.container.get(Agents).save(agent.with_(is_overview_read=False), Actor.system())
        story.observed("the existing Plan seat has no plan visibility binding and owes its overview", None, None)
