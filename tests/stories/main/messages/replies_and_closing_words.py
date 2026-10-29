from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.missing_row import MISSING_ROW
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_closing_turn_of_only_a_face_is_kept_out_and_the_agent_is_told_to_react(story):
    story.agent_closes_its_turn("👍")
    story.expect_agent_told(MessagesNudges.EMOJI_REPLY, emoji="👍")
    story.expect_agent_messages(0)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reply_to_a_message_that_does_not_exist_is_refused(story):
    story.agent_replies(MISSING_ROW, "it is done")
    story.expect_command_refused()
    story.expect_agent_messages(0)
    story.expect_stack(Ready)
