from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import BUILDER_MODE, ORCHESTRATOR_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(StartedPlan, mode=ORCHESTRATOR_MODE, scope=AgentRole.MAIN)
def test_an_orchestrator_starts_a_second_plan_and_both_stay_started(story):
    second_plan = story.user_creates_plan("q", "b")
    third_task = story.user_adds_plan_task(second_plan, "third")
    story.user_approves_plan(second_plan)
    story.agent_runs(f"plan start {second_plan}")
    story.expect_command_passed()
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_plan(second_plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_task(third_task, state=TaskState.OPEN)
    story.expect_stack(Orchestrating, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_builder_with_a_plan_task_in_hand_is_refused_a_second_plan(story):
    second_plan = story.user_creates_plan("q", "b")
    third_task = story.user_adds_plan_task(second_plan, "third")
    story.user_approves_plan(second_plan)
    story.agent_runs(f"plan start {second_plan}")
    story.expect_command_refused()
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_plan(second_plan, state=PlanState.APPROVED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_task(third_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)
