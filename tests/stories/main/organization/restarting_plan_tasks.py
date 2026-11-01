from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_organization_plan_task import PausedOrganizationPlanTask


@story(PausedOrganizationPlanTask, subject=AgentRole.MAIN)
def test_a_user_restarting_an_organization_plan_opens_its_task_for_the_plan_seat(story):
    plan, task = story.plans.first, story.tasks.first

    started = story.user_starts_plan(plan)
    started.expect_viewer_passed()
    shown = story.agent_runs(story.agents.main, f"plan show {plan}")
    shown.expect_command_passed()
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_task_unheld(task)

    seat = story.agent_starts_plan_seat(story.agents.main, plan)
    seat.expect_agent_told(story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha")
    handed_off = story.agent_runs_from_openrig_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handed_off.expect_command_passed()
    story.expect_organization_handoff_pending(plan, task, "domain:alpha")
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_task(story.tasks.second, state=TaskState.BLOCKED, delegated=False)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)


@story(PausedOrganizationPlanTask, subject=AgentRole.MAIN)
def test_an_operator_console_restart_opens_its_task_for_the_plan_seat(story):
    plan, task = story.plans.first, story.tasks.first

    started = story.agent_runs(story.agents.main, f"plan start {plan}")
    started.expect_command_passed()
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_task_unheld(task)

    seat = story.agent_starts_plan_seat(story.agents.main, plan)
    seat.expect_agent_told(story.agents.main, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, task=task, domain="alpha")
    handed_off = story.agent_runs_from_openrig_organization_seat(
        story.agents.main, "plan", f"organization handoff {task} domain:alpha",
    )
    handed_off.expect_command_passed()
    story.expect_organization_handoff_pending(plan, task, "domain:alpha")
    story.expect_task(task, state=TaskState.OPEN, delegated=False)
    story.expect_task(story.tasks.second, state=TaskState.BLOCKED, delegated=False)
    story.expect_stack(story.agents.main, LeadingPlan, FollowingPlan)
