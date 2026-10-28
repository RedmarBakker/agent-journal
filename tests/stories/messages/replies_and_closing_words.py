from tests.stories.fixtures.read_message import ReadMessage
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent


@story(ReadMessage, end=[Ready])
def test_closing_words_that_say_something_new_reach_the_chat(story):
    reply = story.agent_replies_with_number(story.start.message, "the footer is done")
    story.expect_agent_told(MessagesNudges.REPLY_REPEAT_WARNING, n=story.start.message, reply=reply)
    story.expect_message(reply, author="agent", reply_target=story.start.message)
    story.agent_closes_its_turn("next I start the header, which waits on the logo")
    story.expect_agent_not_told(MessagesNudges.REPEATED_CLOSING_TEXT)
    story.expect_agent_messages(2)


@story(WorkingAgent, end=[Ready])
def test_a_closing_turn_of_only_a_face_is_kept_out_and_the_agent_is_told_to_react(story):
    story.agent_closes_its_turn("👍")
    story.expect_agent_told(MessagesNudges.EMOJI_REPLY, emoji="👍")
    story.expect_agent_messages(0)


@story(WorkingAgent, end=[Ready])
def test_a_reply_to_a_message_that_does_not_exist_is_refused(story):
    story.agent_replies(9999, "it is done")
    story.expect_command_refused()
    story.expect_agent_messages(0)
