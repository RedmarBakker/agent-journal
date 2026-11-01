from journal.engine.states.void import Void
from journal.features.workers.states.researching import Researching
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, subject=AgentRole.SUBAGENT)
def test_a_subagent_an_older_journal_left_resting_on_void_is_researching_again_at_its_next_tool_use(story):
    story.an_older_journal_left_the_subagent_on_void(story.agents.subject.agent_id)
    result = story.agent_runs_in_the_shell(story.agents.subject, "ls src")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Void, Researching)
