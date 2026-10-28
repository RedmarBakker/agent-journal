from journal.engine.states.demand_block import DemandBlock
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.messages.messages_options import MessagesOptions
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(MessagesOptions.EDIT_BLOCK_LIMIT, 2)
def test_the_countdown_to_the_write_hold_ends_in_a_last_use_line(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_reads()
    story.expect_agent_told(MessagesNudges.INBOX_COUNTDOWN, messages=message)
    story.agent_reads()
    story.expect_agent_told(MessagesNudges.INBOX_LAST_USE, messages=message)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(MessagesOptions.EDIT_BLOCK_LIMIT, 0)
def test_the_next_write_waits_until_the_message_is_read(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_writes("a.py")
    story.expect_refused(MessagesNudges.INBOX_EDIT_BLOCK, count=1)
    story.expect_stack(Ready, DemandBlock)
    story.agent_reads()
    story.expect_allowed()
    story.agent_creates_task("the header")
    story.expect_command_passed()
    story.agent_reads_message(message)
    story.agent_writes("a.py")
    story.expect_allowed()
    story.expect_stack(Ready)


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(MessagesOptions.EDIT_BLOCK_LIMIT, 0)
def test_the_write_hold_leaves_the_task_in_hand_as_it_was(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_writes("a.py")
    story.expect_stack(Ready, Working, DemandBlock)
    story.agent_reads_message(message)
    story.agent_writes("a.py")
    story.expect_allowed()
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_unread_message_is_named_at_the_stop(story):
    message = story.user_sends_message("is the footer done?")
    story.agent_stops()
    story.expect_agent_told(MessagesNudges.NEW_MESSAGE, n=message)
    story.expect_stack(Ready)
