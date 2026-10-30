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


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_given_whole_to_a_worker_is_delegated_and_not_started_for_the_agent(story):
    story.agent_dispatches_worker_on_plan(story.agents.subject, "Lady Lovelace", story.plans.first)
    story.expect_plan(story.plans.first, state=PlanState.DELEGATED)
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_plan(story.plans.first, state=PlanState.DELEGATED)
    story.expect_task(story.tasks.first, state=TaskState.OPEN)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
