from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from tests.lab.simulated_seats import SimulatedSeats
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class OrganizationDomainRoleTask(OrganizationHubPlan):
    """A started organization plan has a completed task and a current task waiting with its Domain."""

    parent = OrganizationHubPlan
    settings = ((PlansOptions.PLAN_AGENTS, True), (WorkersOptions.MODE, ORCHESTRATOR_MODE))

    def steps(self, story) -> None:
        self.tasks.second = story.user_adds_plan_task(self.plans.first, "task 6 current", "alpha")
        story.user_rewrites_the_brief(self.tasks.second, "- task 6 has its current brief")
        story.user_completes_task(self.tasks.first, "task 5 was already complete")
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        story.openrig = SimulatedSeats()
        runtime = story.app.container.get(SeatRuntime)
        story.monkeypatch.setattr(runtime, "execute", story.openrig.execute)
        story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()
        self.add_domain_seats(story, runtime)
        story.plays_in(BUILDER_MODE)
        seat = story.agent_starts_plan_seat(story.agents.main, self.plans.first)
        seat.expect_agent_told(story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                               task=self.tasks.second, domain="alpha")
        story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview").expect_command_passed()
        story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {self.tasks.second} domain:alpha",
        ).expect_command_passed()

    def add_domain_seats(self, story, runtime: SeatRuntime) -> None:
        rig = f"plan-{self.plans.first}"
        environment = story.app.container.get(Environments).existing(rig)
        organization = story.app.container.get(Organization)
        contracts = organization.reload()
        provider = story.app.container.get(Providers).lookup(story.provider)
        path = story.app.container.get(RigSpecs).write(
            rig, contracts, tuple(domain.id for domain in contracts.domains), story.app.config.root,
            lambda seat: SeatWorker(Actor.agent(""), AgentToken.random(), environment.name, seat.qualified, rig), provider,
        )
        runtime.replace_rig(rig, path)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_task(self.tasks.second, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
