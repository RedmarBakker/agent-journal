from journal.engine.states.compacting import Compacting
from journal.features.messages.messages_nudges import MessagesNudges
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.compacting_task import CompactingTask


@story(CompactingTask, subject=AgentRole.MAIN)
def test_a_message_reaches_an_agent_waiting_over_a_compaction_that_never_started_and_its_next_tool_ends_both(story):
    story.agent_runs(story.agents.subject, "await 'the designs' --until false")
    story.expect_stack(story.agents.subject, Ready, Working, Compacting, ExternalWait)
    story.agent_stops(story.agents.subject)
    message = story.user_sends_message("are the designs in?")
    story.expect_typed(MessagesNudges.NEW_MESSAGE.create(n=message))
    story.agent_reads(story.agents.subject)
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(CompactingTask, subject=AgentRole.MAIN)
def test_a_tool_ending_after_a_compaction_that_never_started_ends_it(story):
    story.agent_has_run_in_the_shell(story.agents.subject, "journal task list")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
