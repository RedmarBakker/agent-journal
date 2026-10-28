from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.started_task import StartedTask


@story(WorkingAgent, end=[Ready, FollowingSequence])
def test_a_comment_on_a_document_asks_for_the_reply_and_the_change_in_the_document(story):
    document = story.agent_writes_a_document("the footer", "## Layout\n\nThe footer holds the links.\n")
    comment = story.user_comments_on("docs", document, "put the copyright in the footer too")
    story.agent_reads_message(comment)
    story.expect_agent_told(MessagesNudges.COMMENT_READ, n=comment)
    story.expect_agent_not_told(MessagesNudges.MESSAGE_READ)


@story(StartedTask, end=[Ready, Working, FollowingSequence])
def test_a_comment_with_a_task_in_hand_leaves_the_task_as_it_was(story):
    document = story.agent_writes_a_document("the footer", "## Layout\n\nThe footer holds the links.\n")
    comment = story.user_comments_on("docs", document, "put the copyright in the footer too")
    story.agent_reads_message(comment)
    story.expect_agent_told(MessagesNudges.COMMENT_READ, n=comment)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
