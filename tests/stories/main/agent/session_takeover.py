from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.started_plan import StartedPlan
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.task_takeover import TaskTakeover


@story(TaskTakeover, mode=BUILDER_MODE)
def test_the_session_that_took_over_reads_the_overview_before_it_writes(story):
    story.agent_writes("footer.py")
    story.expect_refused(BriefingNudges.OVERVIEW_REQUEST)
    story.agent_looks_at_the_overview()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_session_of_the_other_provider_takes_over_too(story):
    story.other_provider_session_starts()
    story.expect_agent_session(story.main_session())
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedPlan, mode=BUILDER_MODE)
def test_a_takeover_keeps_the_followed_plan_in_hand(story):
    story.second_session_starts()
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_stack(Ready, FollowingPlan)


@story(BuildWait, mode=BUILDER_MODE)
def test_a_takeover_while_the_agent_waits_keeps_the_wait(story):
    story.second_session_starts()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, ExternalWait)
