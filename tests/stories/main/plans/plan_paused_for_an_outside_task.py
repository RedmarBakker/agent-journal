from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.choosing_plan_return import ChoosingPlanReturn
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.agent_paused_plan import AgentPausedPlan
from tests.stories.fixtures.main.paused_plan_outside_task import PausedPlanOutsideTask
from tests.stories.fixtures.main.plan_return import PlanReturn


@story(PausedPlanOutsideTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_writes_and_stops_wait_until_the_agent_says_where_it_returns(story):
    story.agent_writes("build.py")
    story.expect_refused(PlansNudges.PLAN_RETURN_QUESTION, n=story.start.plan, task=story.start.fix)
    story.agent_stops()
    story.expect_refused(PlansNudges.PLAN_RETURN_QUESTION, n=story.start.plan, task=story.start.fix)
    story.expect_stack(Ready, Working, ChoosingPlanReturn)


@story(PlanReturn, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_after_yes_the_plan_goes_on_once_the_outside_task_is_done(story):
    story.agent_runs(f"task complete {story.start.fix} --how 'the build passes'")
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_stack(Ready, FollowingPlan)


@story(PausedPlanOutsideTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_no_leaves_the_plan_paused_and_the_outside_task_in_hand(story):
    story.agent_runs(f"plan return {story.start.plan} no")
    story.expect_plan(story.start.plan, state=PlanState.PAUSED)
    story.agent_writes("build.py")
    story.expect_allowed()
    story.expect_task(story.start.fix, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(AgentPausedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_taking_up_a_task_of_the_paused_plan_follows_the_plan_again_and_asks_nothing(story):
    story.agent_runs(f"task start {story.start.second_task}")
    story.agent_writes("footer.py")
    story.expect_agent_not_told(PlansNudges.PLAN_RETURN_QUESTION)
    story.expect_task(story.start.second_task, state=TaskState.STARTED)
    story.expect_stack(Ready, FollowingPlan)
