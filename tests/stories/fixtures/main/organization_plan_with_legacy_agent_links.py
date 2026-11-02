from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import PLAN_AGENT_LINK
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from tests.stories.fixtures.main.organization_plan_with_stale_owner_row import OrganizationPlanWithStaleOwnerRow


class OrganizationPlanWithLegacyAgentLinks(OrganizationPlanWithStaleOwnerRow):
    """An older journal kept both the ended owner-row link and the fresh private Plan-row link."""

    parent = OrganizationPlanWithStaleOwnerRow

    def steps(self, story) -> None:
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        environment = story.app.container.get(Environments).existing(f"plan-{plan.id}")
        fresh = story.app.container.get(AgentEnvironments).prepared(environment, LeadingPlan(plan_id=plan.id), plan.environment_id, Actor.system())
        story.app.container.get(Links).save(Link(source=Ref.build(plan), target=Ref.build(fresh), link_type=PLAN_AGENT_LINK), Actor.system())
        with story.app.container.get(Scope).environment(environment.row_id):
            story.app.container.get(Agents).save(fresh.with_(is_overview_read=False), Actor.system())
        stale = story.app.container.get(Links).targets(plan, PLAN_AGENT_LINK)[0]
        row = story.app.container.get(Agents).global_matching(id=stale.id)[0]
        session = story.session_of(story.organization_seat_agent_in_plan("plan", plan.id))
        with story.app.container.get(Scope).environment(row.environment_id):
            story.app.container.get(Agents).save(row.with_session(session, row.provider), Actor.system())
        story.observed("the legacy journal kept a newer link beside an older session alias", None, None)
