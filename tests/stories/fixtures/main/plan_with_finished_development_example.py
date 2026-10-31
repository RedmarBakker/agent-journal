from datetime import datetime, timezone

from journal.engine.clock import Clock
from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.rig_specs import RigSpecs
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.plans.plans_options import PlansOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from tests.stories.fixtures.main.domain_delivery_setup import setup_domain
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWithFinishedDevelopmentExample(StateFixture):
    """The owner accepted delivery of an organization task and made a second organization plan."""

    stack = (Ready,)
    parent = ReportSizedPlan
    settings = ((PlansOptions.PLAN_AGENTS, True),)

    def steps(self, story) -> None:
        setup_domain(story, self, "l03-example-development", "development", {
            "criterion": "A successful production deployment of the committed revision.",
            "evidence": "production_deployment",
            "target": "production",
        })
        story.user_sets(EstimatesOptions.MODE, "report").expect_viewer_passed()
        main_session = story.main_session()
        story.configure_simulated_openrig()
        self.write_rig_specs(story, "main")
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}").expect_command_passed()
        story.user_approves_plan(self.plans.first).expect_viewer_passed()
        story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()
        self.add_domain_seats(story)
        story.plays_in(BUILDER_MODE)
        plan_seat = story.agent_starts_plan_seat(story.agents.main, self.plans.first)
        plan_seat.expect_agent_told(story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                                    task=self.tasks.first, domain="development")
        story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview").expect_command_passed()
        story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {self.tasks.first} domain:development",
        ).expect_command_passed()
        story.agent_runs_from_organization_seat(
            story.agents.main, "domain:development", f"organization handoff {self.tasks.first} role:development/delivery",
        ).expect_command_passed()
        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.agent_starts_role_session(worker).expect_allowed(worker)
        story.agent_runs_from_openrig_organization_seat(worker, "role:development/delivery", "clock-in").expect_command_passed()
        story.time_travel(seconds=3600)
        story.agent_runs_from_openrig_organization_seat(
            worker, "role:development/delivery", "proof 1 'the production artifact is ready'",
        ).expect_command_passed()
        story.agent_runs_from_openrig_organization_seat(
            worker, "role:development/delivery", "clock-out 'the production artifact is ready'",
        ).expect_command_passed()
        story.agent_runs_from_organization_seat(
            story.agents.main, "domain:development", f"worker check {worker} 1",
        ).expect_command_passed()
        story.agent_runs_from_organization_seat(
            story.agents.main, "domain:development", f"organization handoff {self.tasks.first} plan",
        ).expect_command_passed()
        story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"worker merge {worker}",
        ).expect_command_passed()
        story.time_travel(seconds=3600)
        story.user_presses(f"/journal/plans/{self.plans.first}/delivery", {
            "action": "accept", "evidence": {
                "kind": "production_deployment", "source": "deployment pipeline", "reference": "release-l03",
                "artifact": "revision-l03", "environment": "production", "result": "succeeded",
                "task_ids": [self.tasks.first],
                "occurred_at": datetime.fromtimestamp(story.app.container.get(Clock).held_at, timezone.utc).isoformat(),
            },
        }).expect_viewer_passed()
        story.replace_main_session(main_session, story.provider)
        self.plans.second = story.user_creates_plan("next release", "the next release reaches production")
        story.agent_runs(story.agents.main, f"plan mode {self.plans.second} organization").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.FINISHED, mode=PlanMode.ORGANIZATION)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED, size=3)
        story.expect_plan(self.plans.second, state=PlanState.DRAFT, mode=PlanMode.ORGANIZATION)
        story.expect_stack(story.agents.main, Ready)

    def write_rig_specs(self, story, environment: str) -> None:
        rig = f"plan-{self.plans.first}"
        contracts = story.app.container.get(Organization).reload()
        provider = story.app.container.get(Providers).lookup(story.provider)
        story.app.container.get(RigSpecs).write(
            rig, contracts, tuple(domain.id for domain in contracts.domains), story.app.config.root,
            lambda seat: SeatWorker(Actor.agent(""), AgentToken(f"story-seat-{rig}-{seat.qualified}"), environment, seat.qualified, rig),
            provider,
        )

    def add_domain_seats(self, story) -> None:
        rig = f"plan-{self.plans.first}"
        runtime = story.app.container.get(SeatRuntime)
        environment = story.app.container.get(Environments).existing(rig)
        contracts = story.app.container.get(Organization).reload()
        provider = story.app.container.get(Providers).lookup(story.provider)
        path = story.app.container.get(RigSpecs).write(
            rig, contracts, tuple(domain.id for domain in contracts.domains), story.app.config.root,
            lambda seat: SeatWorker(Actor.agent(""), AgentToken.random(), environment.name, seat.qualified, rig),
            provider,
        )
        plan = story.app.container.get(Plans).global_matching(id=self.plans.first)[0]
        if story.app.container.get(RigStaffing).is_running(plan, provider.name):
            runtime.replace_rig(rig, path)
