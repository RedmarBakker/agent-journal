from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


@story(OrganizationHubPlan, subject=AgentRole.MAIN)
def test_pausing_a_plan_with_its_only_task_in_hand_leaves_it_restartable(story):
    plan, task = story.plans.first, story.tasks.first
    story.agent_runs(story.agents.main, f"plan mode {plan} organization").expect_command_passed()
    story.user_approves_plan(plan).expect_viewer_passed()
    story.agent_runs(story.agents.main, f"plan start {plan}").expect_command_passed()
    story.agent_runs(story.agents.main, f"task start {task}").expect_command_passed()

    paused = story.user_pauses_plan(plan)
    paused.expect_viewer_passed()
    story.expect_plan(plan, state=PlanState.PAUSED)
    story.expect_task(task, state=TaskState.BLOCKED, block_reason=f"plan {plan} was paused")

    started = story.user_starts_plan(plan)
    started.expect_viewer_passed()
    started.expect_agent_not_told(story.agents.main, PlansNudges.PLAN_STALLED, n=plan)
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(task, state=TaskState.OPEN)
    story.expect_stack(story.agents.main, Ready, FollowingPlan)
