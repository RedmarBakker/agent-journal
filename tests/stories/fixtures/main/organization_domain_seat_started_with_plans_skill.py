from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.skills.skills_options import SkillsOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats


class OrganizationDomainSeatStartedWithPlansSkill(OrganizationPlanWithoutDomainSeats):
    """An organization Domain seat starts with the plans skill still due."""

    parent = OrganizationPlanWithoutDomainSeats
    settings = ((SkillsOptions.START_SKILLS, [*SkillsOptions.START_SKILLS.default, "plans"]),)

    def steps(self, story) -> None:
        plan, task = story.plans.first, story.tasks.first
        handed = story.agent_runs_from_plan_organization_seat(
            story.agents.main, "plan", f"organization handoff {task} domain:alpha",
        )
        handed.expect_command_passed()
        domain = story.organization_seat_agent("domain:alpha")
        started = story.agent_starts_organization_seat(domain, "domain:alpha")
        started.expect_allowed(domain)
        story.expect_openrig_seat_environment(domain, "domain:alpha")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.organization_seat_agent("domain:alpha"), LeadingPlan, FollowingPlan)
