from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.agent_at_work import AgentAtWork


@story(AgentAtWork, end=[Ready])
def test_closing_words_that_say_something_new_reach_the_chat(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    reply = story.agent_replies_with_number(message, "the footer is done")
    story.expect_agent_told(MessagesNudges.REPLY_REPEAT_WARNING, n=message, reply=reply)
    story.expect_message(reply, author="agent", reply_target=message)
    story.agent_closes_its_turn("next I start the header, which waits on the logo")
    story.expect_agent_not_told(MessagesNudges.REPEATED_CLOSING_TEXT)
    story.expect_agent_messages(2)


@story(AgentAtWork, end=[Ready])
def test_a_closing_turn_of_only_a_face_is_kept_out_and_the_agent_is_told_to_react(story):
    story.agent_closes_its_turn("👍")
    story.expect_agent_told(MessagesNudges.EMOJI_REPLY, emoji="👍")
    story.expect_agent_messages(0)


@story(AgentAtWork, end=[Ready])
def test_a_reply_to_a_message_that_does_not_exist_is_refused(story):
    story.agent_replies(9999, "it is done")
    story.expect_command_refused()
    story.expect_agent_messages(0)
