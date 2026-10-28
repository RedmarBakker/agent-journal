from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.missing_row import MISSING_ROW
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_message_read_piped_into_a_filter_is_refused(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_runs_in_the_shell(f"journal message read {message} | head -3")
    story.expect_refused(MessagesNudges.FULL_MESSAGE_READ)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_message_read_alone_goes_through(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_runs_in_the_shell(f"journal message read {message}")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_reply_naming_a_row_that_does_not_exist_is_asked_to_correct_it(story):
    reply = story.agent_replies_with_number(story.start.message, f"yes, task {MISSING_ROW} is done")
    story.expect_agent_told(MessagesNudges.MISSING_ROWS, n=reply)
    story.expect_stack(Ready)


@story(ReadMessage, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_users_own_message_cannot_be_linked_by_the_agent(story):
    story.agent_runs(f"message amend-links {story.start.message} task")
    story.expect_command_refused()
    story.expect_stack(Ready)
