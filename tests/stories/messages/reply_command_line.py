from journal.features.messages.messages_nudges import REPLY_COMMAND_SPAN_USES, MessagesNudges
from journal.features.tasks.states.ready import Ready
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.read_message import ReadMessage


@story(ReadMessage, end=[Ready])
def test_a_second_message_read_soon_after_names_only_what_to_do(story):
    story.agent_replies(story.start.message, "not yet")
    second = story.user_sends_message("and the header?")
    story.agent_reads_message(second)
    story.expect_agent_told(MessagesNudges.MESSAGE_READ, n=second)
    story.expect_agent_not_told(MessagesNudges.REPLY_COMMAND)


@story(ReadMessage, end=[Ready])
def test_a_message_read_past_the_span_of_tool_uses_names_the_reply_command_again(story):
    story.agent_replies(story.start.message, "not yet")
    story.agent_reads(count=REPLY_COMMAND_SPAN_USES)
    second = story.user_sends_message("and the header?")
    story.agent_reads_message(second)
    story.expect_agent_told(MessagesNudges.REPLY_COMMAND)
