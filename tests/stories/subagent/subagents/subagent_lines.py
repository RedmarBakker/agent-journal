from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_the_main_agents_new_message_is_never_told_to_the_subagent(story):
    story.user_sends_message("how far is the parser?")
    story.agent_reads()
    story.expect_agent_not_told(MessagesNudges.NEW_MESSAGE)
    story.expect_stack(Void, Researching)
