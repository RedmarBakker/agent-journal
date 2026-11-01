from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_domain_plan_draft import OrganizationDomainPlanDraft


class OrganizationPlanWithDependentDomains(OrganizationDomainPlanDraft):
    """A started plan hands Alpha its task before dependent Beta work can start."""

    parent = OrganizationDomainPlanDraft
    stack = (CoordinatingPlans,)
    settings = ()

    def steps(self, story) -> None:
        added = story.user_presses(
            f"/journal/plans/{self.plans.first}/tasks",
            {
                "title": "Engineering task",
                "brief": "- Engineering follows Alpha",
                "domain": "beta",
                "after": [self.tasks.first],
                "reason": "Engineering starts after Alpha is complete",
            },
        )
        added.expect_viewer_passed()
        self.tasks.second = added.viewer_answer["id"]
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first).expect_viewer_passed()
        story.user_starts_plan(self.plans.first).expect_viewer_passed()
        started = story.agent_starts_plan_seat(story.agents.main, self.plans.first)
        started.expect_agent_told(
            story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
            task=self.tasks.first, domain="alpha",
        )
        started.expect_agent_not_told(
            story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF,
            task=self.tasks.second, domain="beta",
        )
        story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "environment overview").expect_command_passed()
        handoff = story.agent_runs_from_openrig_organization_seat(
            story.agents.main, "plan", f"organization handoff {self.tasks.first} domain:alpha",
        )
        handoff.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_task(self.tasks.second, state=TaskState.OPEN)
        story.expect_organization_handoff_pending(self.plans.first, self.tasks.first, "domain:alpha")
        story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
