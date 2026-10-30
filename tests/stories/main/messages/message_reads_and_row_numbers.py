from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.missing_row import MISSING_ROW
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.read_message import ReadMessage
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_message_read_piped_into_a_filter_is_refused(story):
    message = story.user_sends_message("is the footer done?")
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal message read {message} | head -3")
    result.expect_refused(story.agents.subject, MessagesNudges.FULL_MESSAGE_READ)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_message_read_alone_goes_through(story):
    message = story.user_sends_message("is the footer done?")
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal message read {message}")
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(ReadMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reply_naming_a_row_that_does_not_exist_is_asked_to_correct_it(story):
    reply = story.agent_replies_with_number(story.agents.subject, story.messages.first, f"yes, task {MISSING_ROW} is done")
    story.last_step.expect_agent_told(story.agents.subject, MessagesNudges.MISSING_ROWS, n=reply)
    story.expect_stack(story.agents.subject, Ready)


@story(ReadMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_users_own_message_cannot_be_linked_by_the_agent(story):
    result = story.agent_runs(story.agents.subject, f"message amend-links {story.messages.first} task")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)

