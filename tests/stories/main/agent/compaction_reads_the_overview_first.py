from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.briefing.states.reading_overview import ReadingOverview
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.compacted_task import CompactedTask
from tests.stories.fixtures.main.started_task import StartedTask


@story(CompactedTask, mode=BUILDER_MODE)
def test_after_a_compaction_a_write_waits_for_the_overview(story):
    story.agent_writes("footer.py")
    story.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, ReadingOverview)


@story(CompactedTask, mode=BUILDER_MODE)
def test_after_a_compaction_a_journal_command_other_than_the_overview_waits_too(story):
    story.agent_runs_in_the_shell("journal task list")
    story.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    story.agent_reads()
    story.expect_refused(BriefingNudges.OVERVIEW_FIRST)
    story.expect_stack(Ready, Working, ReadingOverview)


@story(CompactedTask, mode=BUILDER_MODE)
def test_the_overview_ends_the_wait_and_the_work_goes_on(story):
    story.agent_looks_at_the_overview()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(CompactedTask, mode=BUILDER_MODE)
def test_a_stop_before_the_overview_is_refused(story):
    story.agent_stops()
    story.expect_refused(BriefingNudges.OVERVIEW_STOP)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working, ReadingOverview)


@story(StartedTask, mode=BUILDER_MODE)
def test_a_resumed_session_needs_no_overview(story):
    story.agent_resumes_the_session()
    story.agent_writes("footer.py")
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
