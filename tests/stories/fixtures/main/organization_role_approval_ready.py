from pathlib import Path

from journal.engine.states.void import Void
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.plans.plans_options import PlansOptions
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.providers.providers import Providers
from journal.repositories.plans import Plans
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from tests.stories.fixtures.main.new_session import NewSession


class OrganizationRoleApprovalReady(NewSession):
    """A journal Role worker holds an organization task under a destructive-action approval policy."""

    parent = NewSession
    settings = (
        (OrganizationOptions.FOLDER, str(Path(__file__).resolve().with_name("organization_role_approval"))),
        (PlansOptions.PLAN_AGENTS, True),
    )

    def steps(self, story) -> None:
        story.configure_simulated_openrig()
        contracts = story.app.container.get(Organization).reload()
        self.plans.first = story.user_creates_plan("Approval plan", "Approval plan")
        self.tasks.first = story.user_adds_plan_task(self.plans.first, "Check approval behavior", "alpha")
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first).expect_viewer_passed()
        rig = story.plan_rig_name(self.plans.first)
        provider = story.app.container.get(Providers).lookup(story.provider)
        story.app.container.get(RigSpecs).write(
            rig, contracts, tuple(domain.id for domain in contracts.domains), story.app.config.root,
            lambda seat: SeatWorker(
                Actor.agent(""), AgentToken(f"story-seat-{rig}-{seat.qualified}"), "main", seat.qualified, rig,
            ),
            provider,
        )
        story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()
        story.agent_starts_plan_seat(story.agents.main, self.plans.first).expect_allowed(story.agents.main)
        story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview").expect_command_passed()
        story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {self.tasks.first} domain:alpha",
        ).expect_command_passed()
        domain = story.organization_seat_agent_in_plan("domain:alpha", self.plans.first)
        story.agent_starts_organization_seat_in_plan(domain, "domain:alpha", self.plans.first).expect_allowed(domain)
        story.agent_runs_from_openrig_organization_seat(domain, "domain:alpha", "organization inbox").expect_command_passed()
        story.agent_runs_from_openrig_organization_seat(
            domain, "domain:alpha", f"organization handoff {self.tasks.first} role:alpha/builder",
        ).expect_command_passed()
        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.agent_starts_role_session(worker).expect_allowed(worker)
        story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.STARTED, delegated=True)
        story.expect_worker(self.workers.first, state=WorkerState.READY)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
