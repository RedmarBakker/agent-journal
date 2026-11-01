from journal.features.messages.messages_nudges import REPLY_COMMAND_SPAN_USES, MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage


@story(ReadMessage, subject=AgentRole.MAIN)
def test_a_second_message_read_soon_after_names_only_what_to_do(story):
    story.agent_replies(story.agents.subject, story.messages.first, "not yet")
    second = story.user_sends_message("and the header?")
    result = story.agent_reads_message(story.agents.subject, second)
    result.expect_agent_told(story.agents.subject, MessagesNudges.MESSAGE_READ, n=second)
    result.expect_agent_not_told(story.agents.subject, MessagesNudges.REPLY_COMMAND)
    story.expect_stack(story.agents.subject, Ready)


@story(ReadMessage, subject=AgentRole.MAIN)
def test_a_message_read_past_the_span_of_tool_uses_names_the_reply_command_again(story):
    story.agent_replies(story.agents.subject, story.messages.first, "not yet")
    story.agent_reads(story.agents.subject, count=REPLY_COMMAND_SPAN_USES)
    second = story.user_sends_message("and the header?")
    result = story.agent_reads_message(story.agents.subject, second)
    result.expect_agent_told(story.agents.subject, MessagesNudges.REPLY_COMMAND)
    story.expect_stack(story.agents.subject, Ready)
