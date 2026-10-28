from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.compacted_task import CompactedTask
from tests.stories.fixtures.main.sequence_run import SequenceRun
from tests.stories.fixtures.main.started_plan import StartedPlan


@story(StartedPlan, mode=BUILDER_MODE)
def test_a_followed_plan_survives_a_compaction(story):
    story.context_is_compacted()
    story.expect_stack(Ready, FollowingPlan, ReadingOverview)
    story.agent_looks_at_the_overview()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_plan(story.start.plan, state=PlanState.STARTED)
    story.expect_task(story.start.first_task, state=TaskState.STARTED)
    story.expect_stack(Ready, FollowingPlan)


@story(SequenceRun, mode=BUILDER_MODE)
def test_a_running_sequence_says_its_step_again_after_the_overview(story):
    story.context_is_compacted()
    story.agent_looks_at_the_overview()
    story.expect_agent_told(SequencesNudges.PENDING_STEP, n=story.start.sequence, step=1)
    story.expect_stack(Ready, FollowingSequence)


@story(CompactedTask, mode=BUILDER_MODE)
def test_a_second_compaction_before_the_overview_asks_for_it_once(story):
    story.context_is_compacted()
    story.expect_stack(Ready, Working, ReadingOverview)
    story.agent_looks_at_the_overview()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(BuildWait, mode=BUILDER_MODE)
def test_a_waiting_agent_that_is_compacted_goes_back_to_its_wait_after_the_overview(story):
    story.context_is_compacted()
    story.agent_looks_at_the_overview()
    story.agent_stops()
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, ExternalWait)
