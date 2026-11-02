from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from tests.stories.fixtures.main.organization_domain_plan_draft import OrganizationDomainPlanDraft


class OrganizationPlanEnvironmentPrepared(OrganizationDomainPlanDraft):
    """An organization plan has a committed environment ready for its Plan agent."""

    parent = OrganizationDomainPlanDraft

    def steps(self, story) -> None:
        source = story.app.container.get(Environments).existing("main")
        story.app.container.get(AgentEnvironments).made(f"plan-{self.plans.first}", source.row_id, Actor.system(), "plan")
