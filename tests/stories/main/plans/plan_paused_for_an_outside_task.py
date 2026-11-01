from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.choosing_plan_return import ChoosingPlanReturn
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.agent_paused_plan import AgentPausedPlan
from tests.stories.fixtures.main.paused_plan_outside_task import PausedPlanOutsideTask
from tests.stories.fixtures.main.plan_return import PlanReturn


@story(PausedPlanOutsideTask, subject=AgentRole.MAIN)
def test_writes_and_stops_wait_until_the_agent_says_where_it_returns(story):
    result = story.agent_writes(story.agents.subject, "build.py")
    result.expect_refused(story.agents.subject, PlansNudges.PLAN_RETURN_QUESTION, n=story.plans.first, task=story.tasks.outside)
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, PlansNudges.PLAN_RETURN_QUESTION, n=story.plans.first, task=story.tasks.outside)
    story.expect_stack(story.agents.subject, Ready, Working, ChoosingPlanReturn)


@story(PlanReturn, subject=AgentRole.MAIN)
def test_after_yes_the_plan_goes_on_once_the_outside_task_is_done(story):
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.outside} --how 'the build passes'")
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PausedPlanOutsideTask, subject=AgentRole.MAIN)
def test_no_leaves_the_plan_paused_and_the_outside_task_in_hand(story):
    story.agent_runs(story.agents.subject, f"plan return {story.plans.first} no")
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    result = story.agent_writes(story.agents.subject, "build.py")
    result.expect_allowed()
    story.expect_task(story.tasks.outside, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(AgentPausedPlan, subject=AgentRole.MAIN)
def test_taking_up_a_task_of_the_paused_plan_follows_the_plan_again_and_asks_nothing(story):
    story.agent_runs(story.agents.subject, f"task start {story.tasks.second}")
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_agent_not_told(story.agents.subject, PlansNudges.PLAN_RETURN_QUESTION)
    story.expect_task(story.tasks.second, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
