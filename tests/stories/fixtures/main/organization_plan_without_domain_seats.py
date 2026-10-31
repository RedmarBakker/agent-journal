from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan

TASK_BRIEF = "- the current brief is met"


class OrganizationPlanWithoutDomainSeats(OrganizationHubPlan):
    """A started organization plan rig has only its Plan seat."""

    settings = (*OrganizationHubPlan.settings, (PlansOptions.PLAN_AGENTS, True), (WorkersOptions.MODE, ORCHESTRATOR_MODE))
    task_domain = "alpha"

    def steps(self, story) -> None:
        super().steps(story)
        story.user_rewrites_the_brief(self.tasks.first, TASK_BRIEF)
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        story.monkeypatch.setattr(WorkerRunner, "start", story.app.original_worker_start)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()
        story.plays_in(BUILDER_MODE)
        seat = story.agent_starts_plan_seat(story.agents.main, self.plans.first)
        seat.expect_agent_told(story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
                               task=self.tasks.first, domain="alpha")
        story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
