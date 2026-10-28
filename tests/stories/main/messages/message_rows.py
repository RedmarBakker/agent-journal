from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_agents_reply_is_a_message_row_of_its_own_answering_the_users_and_no_comment(story):
    story.agent_replies(story.start.message, "Hello back.")
    reply = story.newest("messages")
    story.expect_message(reply, author="agent", reply_target=story.start.message, text="Hello back.", acknowledgement=False)
    story.user_opens("/journal/messages?comments=1")
    story.expect_viewer_count("rows", 0)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reply_in_the_column_hangs_under_its_comment_and_one_in_the_chat_is_talk(story):
    footer = story.agent_creates_task("the footer")
    comment = story.user_comments_on("tasks", footer, "is the footer fixed?")
    column_reply = story.user_replies_in_the_column("tasks", footer, comment, "and the header?")
    story.expect_message(column_reply, reply_target=comment, comments_on=[f"tasks:{footer}"])
    story.agent_replies(comment, "Yes, both are fixed.")
    story.user_opens("/journal/messages?comments=1")
    story.expect_viewer_rows("rows", "author", ["user", "user"])
    chat_reply = story.user_replies_in_the_chat(comment, "Good, then the menu next.")
    story.expect_message(chat_reply, reply_target=comment, comments_on=[])
    story.expect_stack(Ready)


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_same_face_again_takes_the_reaction_off(story):
    story.user_reacts(story.start.message, "👍")
    story.user_opens("/journal/reactions")
    story.expect_viewer_rows("rows", "emoji", ["👍"])
    story.user_reacts(story.start.message, "👍")
    story.user_opens("/journal/reactions")
    story.expect_viewer_count("rows", 0)
    story.expect_stack(Ready)
