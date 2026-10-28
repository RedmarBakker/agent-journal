from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_whose_every_remaining_task_is_blocked_blocks_itself_and_opens_with_it(story):
    story.agent_runs(f"task block {story.start.second_task} 'waits on the designer'")
    story.agent_runs(f"task complete {story.start.first_task} --how done")
    story.expect_plan(story.start.plan, state=PlanState.BLOCKED)
    story.expect_agent_told(PlansNudges.PLAN_BLOCKED, n=story.start.plan)
    story.agent_runs(f"task unblock {story.start.second_task}")
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_agent_told(PlansNudges.PLAN_REOPENED, n=story.start.plan)
    story.expect_stack(Ready, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_blocked_with_no_reason_is_refused(story):
    story.agent_runs(f"plan block {story.start.plan}")
    story.expect_command_refused()
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)
