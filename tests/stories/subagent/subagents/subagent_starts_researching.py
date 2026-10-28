from journal.engine.states.void import Void
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.researching import Researching
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.subagent.started_subagent import StartedSubagent


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_subagent_works_on_a_stack_of_its_own_beside_the_main_agent(story):
    story.agent_reads()
    story.expect_allowed()
    story.expect_main_stack(Ready)
    story.expect_stack(Void, Researching)


@story(StartedSubagent, mode=BUILDER_MODE, scope=AgentRole.SUBAGENT)
def test_a_subagent_writes_while_the_main_agent_owes_a_reply(story):
    message = story.user_sends_message("how far is the parser?")
    story.main_agent_runs(f"message read {message}")
    story.agent_writes("notes.md")
    story.expect_allowed()
    story.expect_agent_not_told(MessagesNudges.MESSAGE_READ)
    story.expect_stack(Void, Researching)
