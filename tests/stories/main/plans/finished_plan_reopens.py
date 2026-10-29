from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.finished_plan import FinishedPlan


@story(FinishedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_task_added_to_a_finished_plan_reopens_it_and_plan_start_takes_it_up(story):
    added = story.user_adds_plan_task(story.fixture.plan, "the footer links")
    story.expect_agent_told(story.agents.subject, PlansNudges.PLAN_REOPENED, n=story.fixture.plan)
    story.expect_agent_not_told(story.agents.subject, PlansNudges.PLAN_STALLED)
    story.expect_task(added, state=TaskState.OPEN)
    story.agent_runs(story.agents.subject, f"plan start {story.fixture.plan}")
    story.expect_plan(story.fixture.plan, state=PlanState.STARTED)
    story.expect_task(added, state=TaskState.STARTED)
    story.expect_task(story.fixture.first_task, state=TaskState.COMPLETED)
    story.expect_task(story.fixture.second_task, state=TaskState.COMPLETED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)
