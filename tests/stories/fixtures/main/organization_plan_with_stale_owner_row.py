from journal.engine.states.ended import Ended
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.agent import Agent
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_AGENT_LINK, Plans
from journal.support.actor import Actor
from tests.stories.fixtures.main.organization_plan_with_domain_seats import OrganizationPlanWithDomainSeats


class OrganizationPlanWithStaleOwnerRow(OrganizationPlanWithDomainSeats):
    """A started plan retains an older link to an ended owner-environment row."""

    parent = OrganizationPlanWithDomainSeats

    def steps(self, story) -> None:
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        links = story.app.container.get(Links)
        for link in links.all_matching(source=Ref.build(plan), link_type=PLAN_AGENT_LINK):
            links.delete(link, Actor.system())
        floor, ended = LeadingPlan(plan_id=plan.row_id), Ended()
        stale = story.app.container.get(Agents).save(Agent(
            environment_id=plan.environment_id, provider=story.provider, state=ended.name,
            stack=({"state": floor.name, "data": floor.serialized()}, {"state": ended.name, "data": {}}),
        ), Actor.system())
        links.save(Link(source=Ref.build(plan), target=Ref.build(stale), link_type=PLAN_AGENT_LINK), Actor.system())
        story.observed("the plan retains an ended owner row's old link", None, None)
