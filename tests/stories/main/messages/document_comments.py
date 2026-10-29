from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.written_document import WrittenDocument


@story(WrittenDocument, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_comment_on_a_document_asks_for_the_reply_and_the_change_in_the_document(story):
    comment = story.user_comments_on("docs", story.fixture.document, "put the copyright in the footer too")
    story.agent_reads_message(story.agents.subject, comment)
    story.expect_agent_told(story.agents.subject, MessagesNudges.COMMENT_READ, n=comment)
    story.expect_agent_not_told(story.agents.subject, MessagesNudges.MESSAGE_READ)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(StartedTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_comment_with_a_task_in_hand_leaves_the_task_as_it_was(story):
    document = story.agent_writes_a_document(story.agents.subject, "the footer", "the footer", "## Layout\n\nThe footer holds the links.\n")
    comment = story.user_comments_on("docs", document, "put the copyright in the footer too")
    story.agent_reads_message(story.agents.subject, comment)
    story.expect_agent_told(story.agents.subject, MessagesNudges.COMMENT_READ, n=comment)
    story.expect_task(story.fixture.started_task, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working, FollowingSequence)
