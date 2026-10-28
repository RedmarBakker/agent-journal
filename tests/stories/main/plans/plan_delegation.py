from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(PlanApproved, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_given_whole_to_a_worker_is_delegated_and_not_started_for_the_agent(story):
    story.agent_dispatches_worker_on_plan("Lady Lovelace", story.start.plan)
    story.expect_plan(story.start.plan, state=PlanState.DELEGATED)
    story.agent_stops()
    story.expect_allowed()
    story.expect_plan(story.start.plan, state=PlanState.DELEGATED)
    story.expect_task(story.start.first_task, state=TaskState.OPEN)
    story.expect_task(story.start.second_task, state=TaskState.OPEN)
    story.expect_stack(Ready, ExternalWait)


@story(StartedPlan, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_plan_with_one_task_given_to_a_worker_while_the_agent_holds_another_stays_started(story):
    story.agent_dispatches_worker("Lady Lovelace", story.start.second_task)
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_stack(Ready, FollowingPlan, ExternalWait)
