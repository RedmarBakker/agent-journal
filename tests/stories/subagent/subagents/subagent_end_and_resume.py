from journal.engine.states.ended import Ended
from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_an_ended_subagent_is_back_at_its_research_at_its_next_tool_use(story):
    story.subagent_ends(story.agents.subagent.agent_id)
    story.expect_stack(story.agents.subject, Void, Researching, Ended)
    story.agent_reads(story.agents.subject)
    story.expect_allowed()
    story.expect_stack(story.agents.subject, Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, subject=AgentRole.SUBAGENT)
def test_the_main_sessions_end_ends_its_subagent_too(story):
    story.agent_ends_the_session(story.agents.main)
    story.expect_stack(story.agents.main, Ready, Ended)
    story.expect_stack(story.agents.subject, Void, Researching, Ended)
