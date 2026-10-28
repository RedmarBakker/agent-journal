from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_second_reply_with_the_same_words_to_the_same_message_is_not_sent_again(story):
    story.agent_replies(story.start.message, "Looking now.")
    story.agent_replies(story.start.message, "Looking now.")
    story.expect_command_text("already has this reply in the chat: not sent again")
    story.expect_agent_messages(1)
    story.expect_stack(Ready)


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reply_the_user_edited_since_keeps_the_key_of_its_words_so_they_are_never_sent_again(story):
    story.agent_replies(story.start.message, "Looking at the footer now.")
    reply = story.newest("messages")
    story.user_edits_message(reply, "Looking at the footer, task 3, now.")
    story.agent_replies(story.start.message, "Looking at the footer now.")
    story.expect_command_text("already has this reply in the chat: not sent again")
    story.expect_agent_messages(1)
    story.expect_stack(Ready)
