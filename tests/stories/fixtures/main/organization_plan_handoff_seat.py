from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan
from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats


class OrganizationPlanHandoffSeat(OrganizationPlanWithoutDomainSeats):
    """The Plan seat has started on its organization plan and task."""

    parent = OrganizationPlanWithoutDomainSeats
    settings = ()

    def start_plan_seat(self, story) -> None:
        seat = story.agent_starts_plan_seat(story.agents.main, self.plans.first)
        seat.expect_agent_told(story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                               task=self.tasks.first, domain="alpha")
        overview = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview")
        overview.expect_command_passed()

    def steps(self, story) -> None:
        self.add_domain_seats(story, story.app.container.get(SeatRuntime))
        boards = story.agent_runs(story.agents.main, "organization plans")
        boards.expect_command_passed()
        boards.expect_command_text("no plans")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


class DelegatedOrganizationPlanHandoffSeat(OrganizationPlanHandoffSeat):
    """The Plan seat starts while its open Domain task is delegated to a worker."""

    parent = OrganizationHubPlan
    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        OrganizationHubPlan.steps(self, story)
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        self.workers.first = story.agent_dispatches_worker_on_plan(story.agents.main, "Lady Lovelace", self.plans.first)
        story.user_sets(PlansOptions.PLAN_AGENTS, True)
        story.configure_simulated_openrig()
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()
        self.add_domain_seats(story, story.app.container.get(SeatRuntime))
        story.plays_in(BUILDER_MODE)
        self.start_plan_seat(story)

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, delegated=True)
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
