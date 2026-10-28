from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
def test_the_users_approval_is_told_to_the_agent(story):
    plan = story.user_creates_plan("the site", "the site is built")
    story.user_adds_plan_task(plan, "the grid")
    story.user_approves_plan(plan)
    story.expect_agent_told(PlansNudges.PLAN_APPROVED, n=plan)
    story.expect_plan(plan, state=PlanState.APPROVED)
    story.expect_stack(Ready)


@story(StartedPlan, mode=BUILDER_MODE)
def test_the_agent_cancelling_its_plan_cancels_the_open_tasks_and_frees_the_stack(story):
    story.agent_runs(f"plan cancel {story.start.plan}")
    story.expect_plan(story.start.plan, state=PlanState.CANCELLED)
    story.expect_task(story.start.first_task, state=TaskState.CANCELLED)
    story.expect_task(story.start.second_task, state=TaskState.CANCELLED)
    story.expect_stack(Ready)
