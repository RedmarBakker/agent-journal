from journal.engine.states.ended import Ended
from journal.features.briefing.listeners.end_silent_sessions import SILENCE_SECONDS
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_session_silent_for_less_than_its_span_is_kept(story):
    story.agent_is_quiet_just_under(SILENCE_SECONDS)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_retired_session_that_speaks_again_is_back_at_its_work(story):
    story.agent_is_quiet_past(SILENCE_SECONDS)
    story.expect_stack(Ready, Working, Ended)
    story.agent_reads()
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
