from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.agent_at_work import AgentAtWork
from tests.stories.fixtures.task_in_hand import TaskInHand


@story(AgentAtWork, end=[Ready])
def test_a_message_read_piped_into_a_filter_is_refused(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_runs_in_the_shell(f"journal message read {message} | head -3")
    story.expect_refused(MessagesNudges.FULL_MESSAGE_READ)


@story(AgentAtWork, end=[Ready])
def test_a_message_read_alone_goes_through(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_runs_in_the_shell(f"journal message read {message}")
    story.expect_allowed()


@story(AgentAtWork, end=[Ready])
def test_a_reply_naming_a_row_that_does_not_exist_is_asked_to_correct_it(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads_message(message)
    reply = story.agent_replies_with_number(message, "yes, task 9999 is done")
    story.expect_agent_told(MessagesNudges.MISSING_ROWS, n=reply)


@story(AgentAtWork, end=[Ready])
def test_the_users_own_message_cannot_be_linked_by_the_agent(story):
    message = story.user_sends_message("see 3 and 4")
    story.agent_reads_message(message)
    story.agent_runs(f"message amend-links {message} task")
    story.expect_command_refused()
