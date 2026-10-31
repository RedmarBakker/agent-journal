from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.outside_task import OutsideTask
from tests.stories.fixtures.main.paused_plan import PausedPlan


@story(OutsideTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_user_pausing_the_plan_meanwhile_leaves_the_outside_task_in_hand(story):
    story.user_pauses_plan(story.plans.first)
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    result = story.agent_stops(story.agents.subject)
    result.expect_refused(story.agents.subject, TasksNudges.TASK_CONTINUATION)
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.outside} --how done")
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    story.expect_stack(story.agents.subject, Ready)


@story(OutsideTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_plan_carries_on_after_the_outside_task_completes(story):
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.outside} --how done")
    story.expect_task(story.tasks.outside, state=TaskState.COMPLETED)
    story.expect_plan(story.plans.first, state=PlanState.STARTED)
    story.expect_stack(story.agents.subject, Ready, FollowingPlan)


@story(PausedPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_the_user_paused_stays_quiet_at_the_stop(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_allowed()
    story.expect_task(story.tasks.first, state=TaskState.BLOCKED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_plan(story.plans.first, state=PlanState.PAUSED)
    story.expect_stack(story.agents.subject, Ready)
