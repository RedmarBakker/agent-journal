from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_row_docks_above_the_chat_by_noun_and_number_in_either_order_once(story):
    notes = story.agent_creates_briefed_task("write the notes", "what and where")
    story.agent_runs(f"task {notes} dock")
    story.expect_command_text(f"Task {notes}: write the notes docked above the chat")
    story.agent_runs(f"task dock {notes}")
    story.expect_docked_cards(f"Task {notes}: write the notes")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_row_that_does_not_exist_is_named_when_asked_to_dock(story):
    story.agent_runs("task 12 dock")
    story.expect_command_refused()
    story.expect_command_text("12")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_undocked_row_leaves_the_chat_and_cannot_be_undocked_again(story):
    notes = story.agent_creates_task("write the notes")
    story.agent_runs(f"task dock {notes}")
    story.agent_runs(f"task undock {notes}")
    story.expect_command_text(f"Task {notes}: write the notes undocked")
    story.expect_docked_cards()
    story.agent_runs(f"task {notes} undock")
    story.expect_command_text("is not docked")
    story.expect_stack(Ready)
