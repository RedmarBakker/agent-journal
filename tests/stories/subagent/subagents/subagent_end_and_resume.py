from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE)
def test_an_ended_subagent_is_back_at_its_research_at_its_next_tool_use(story):
    story.subagent_ends(story.start.subagent)
    story.expect_stack(Void, Researching, Ended)
    story.agent_reads()
    story.expect_allowed()
    story.expect_stack(Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE)
def test_the_main_sessions_end_ends_its_subagent_too(story):
    story.main_agent_ends_the_session()
    story.expect_main_stack(Ready, Ended)
    story.expect_stack(Void, Researching, Ended)
