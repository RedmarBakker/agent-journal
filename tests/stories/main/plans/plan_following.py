from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(StartedPlan, mode=BUILDER_MODE)
def test_a_plans_tasks_follow_in_order_until_it_finishes(story):
    story.agent_runs(f"task complete {story.start.first_task} --how done")
    story.expect_task(story.start.second_task, state=TaskState.STARTED)
    story.agent_stops()
    story.expect_refused(TasksNudges.TASK_CONTINUATION)
    story.agent_runs(f"task complete {story.start.second_task} --how done")
    story.expect_plan(story.start.plan, state=PlanState.FINISHED)
    story.expect_agent_told(PlansNudges.PLAN_FINISHED, n=story.start.plan)
    story.expect_stack(Ready)


@story(PlanApproved, mode=BUILDER_MODE)
def test_starting_an_approved_plan_puts_its_first_task_in_hand(story):
    story.agent_runs(f"plan start {story.start.plan}")
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)


@story(PlanApproved, mode=BUILDER_MODE)
def test_an_approved_plan_starts_by_itself_at_a_session_start(story):
    story.agent_resumes_the_session()
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_stack(Ready, FollowingPlan)


@story(StartedPlan, mode=BUILDER_MODE)
def test_a_paused_plan_task_resumed_carries_on_the_plan(story):
    story.agent_runs(f"task pause {story.start.first_task} 'a look at the logs first'")
    story.agent_runs(f"task resume {story.start.first_task}")
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_stack(Ready, FollowingPlan)
