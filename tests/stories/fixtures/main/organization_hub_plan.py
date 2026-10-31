from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.organization.support.seat_worker import SeatWorker
from journal.models.plan_state import PlanState
from journal.providers.providers import Providers
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from tests.stories.fixtures.main.organization_setup import OrganizationSetup


class OrganizationHubPlan(OrganizationSetup):
    """A draft plan with one task and an organization with two Domains and three plan Roles."""

    parent = OrganizationSetup
    settings = ()
    task_domain = ""

    def steps(self, story) -> None:
        story.configure_simulated_openrig()
        self.plans.first = story.user_creates_plan("p", "b")
        self.tasks.first = story.user_adds_plan_task(self.plans.first, "first", self.task_domain)
        rig = story.plan_rig_name(story.plans.first)
        contracts = story.app.container.get(Organization).reload()
        domains = tuple(domain.id for domain in contracts.domains)
        provider = story.app.container.get(Providers).lookup(story.provider)
        story.app.container.get(RigSpecs).write(
            rig, contracts, domains, story.app.config.root,
            lambda seat: SeatWorker(Actor.agent(""), AgentToken(f"story-seat-{rig}-{seat.qualified}"), "main", seat.qualified, rig),
            provider,
        )

    def expected(self, story) -> None:
        super().expected(story)
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_organization_domains("alpha", "beta")

    def add_domain_seats(self, story, runtime: SeatRuntime) -> None:
        rig = story.plan_rig_name(self.plans.first)
        environment = story.app.container.get(Environments).existing(f"plan-{self.plans.first}")
        contracts = story.app.container.get(Organization).reload()
        provider = story.app.container.get(Providers).lookup(story.provider)
        path = story.app.container.get(RigSpecs).write(
            rig, contracts, tuple(domain.id for domain in contracts.domains), story.app.config.root,
            lambda seat: SeatWorker(Actor.agent(""), AgentToken.random(), environment.name, seat.qualified, rig), provider,
        )
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        if story.app.container.get(RigStaffing).is_running(plan, provider.name):
            runtime.replace_rig(rig, path)
