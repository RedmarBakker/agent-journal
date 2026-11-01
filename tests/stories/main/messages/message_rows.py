from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(ReadMessage, subject=AgentRole.MAIN)
def test_the_agents_reply_is_a_message_row_of_its_own_answering_the_users_and_no_comment(story):
    story.agent_replies(story.agents.subject, story.messages.first, "Hello back.")
    reply = story.newest("messages")
    story.expect_message(reply, author="agent", reply_target=story.messages.first, text="Hello back.", acknowledgement=False)
    result = story.user_opens("/journal/messages?comments=1")
    result.expect_viewer_count("rows", 0)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_reply_in_the_column_hangs_under_its_comment_and_one_in_the_chat_is_talk(story):
    footer = story.agent_creates_task(story.agents.subject, "the footer")
    comment = story.user_comments_on("tasks", footer, "is the footer fixed?")
    column_reply = story.user_replies_in_the_column("tasks", footer, comment, "and the header?")
    story.expect_message(column_reply, reply_target=comment, comments_on=[f"tasks:{footer}"])
    story.agent_replies(story.agents.subject, comment, "Yes, both are fixed.")
    result = story.user_opens("/journal/messages?comments=1")
    result.expect_viewer_rows("rows", "author", ["user", "user"])
    chat_reply = story.user_replies_in_the_chat(comment, "Good, then the menu next.")
    story.expect_message(chat_reply, reply_target=comment, comments_on=[])
    story.expect_stack(story.agents.subject, Ready)


@story(ReadMessage, subject=AgentRole.MAIN)
def test_the_same_face_again_takes_the_reaction_off(story):
    story.user_reacts(story.messages.first, "👍")
    result = story.user_opens("/journal/reactions")
    result.expect_viewer_rows("rows", "emoji", ["👍"])
    story.user_reacts(story.messages.first, "👍")
    result = story.user_opens("/journal/reactions")
    result.expect_viewer_count("rows", 0)
    story.expect_stack(story.agents.subject, Ready)
