from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.missing_row import MISSING_ROW
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_closing_words_after_a_reply_in_the_same_turn_are_kept_out(story):
    story.agent_is_prompted("is the footer done?")
    reply = story.agent_replies_with_number(story.start.message, "the footer is done")
    story.expect_agent_told(MessagesNudges.REPLY_REPEAT_WARNING, n=story.start.message, reply=reply)
    story.expect_message(reply, author="agent", reply_target=story.start.message)
    story.agent_closes_its_turn("next I start the header, which waits on the logo")
    story.expect_newest_agent_message("the footer is done")
    story.expect_stack(Ready)


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_closing_words_of_a_later_turn_reach_the_chat(story):
    story.agent_replies(story.start.message, "the footer is done")
    story.agent_is_prompted_in_a_new_turn("go on")
    story.agent_closes_its_turn("next I start the header, which waits on the logo")
    story.expect_newest_agent_message("next I start the header, which waits on the logo")
    story.expect_stack(Ready)


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
