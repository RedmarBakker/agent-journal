from tests.stories.fixtures.read_message import ReadMessage
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.builder.missing_row import MISSING_ROW
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent
from tests.stories.fixtures.started_task import StartedTask


@story(WorkingAgent, end=[Ready])
def test_a_message_read_piped_into_a_filter_is_refused(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_runs_in_the_shell(f"journal message read {message} | head -3")
    story.expect_refused(MessagesNudges.FULL_MESSAGE_READ)


@story(WorkingAgent, end=[Ready])
def test_a_message_read_alone_goes_through(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_runs_in_the_shell(f"journal message read {message}")
    story.expect_allowed()


@story(ReadMessage, end=[Ready])
def test_a_reply_naming_a_row_that_does_not_exist_is_asked_to_correct_it(story):
    reply = story.agent_replies_with_number(story.start.message, f"yes, task {MISSING_ROW} is done")
    story.expect_agent_told(MessagesNudges.MISSING_ROWS, n=reply)


@story(ReadMessage, end=[Ready])
def test_the_users_own_message_cannot_be_linked_by_the_agent(story):
    story.agent_runs(f"message amend-links {story.start.message} task")
    story.expect_command_refused()
