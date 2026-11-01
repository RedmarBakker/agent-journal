from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_row_docks_above_the_chat_by_noun_and_number_in_either_order_once(story):
    notes = story.agent_creates_briefed_task(story.agents.subject, "write the notes", "what and where")
    result = story.agent_runs(story.agents.subject, f"task {notes} dock")
    result.expect_command_text(f"Task {notes}: write the notes docked above the chat")
    story.agent_runs(story.agents.subject, f"task dock {notes}")
    story.expect_docked_cards(f"Task {notes}: write the notes")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_row_that_does_not_exist_is_named_when_asked_to_dock(story):
    result = story.agent_runs(story.agents.subject, "task 12 dock")
    result.expect_command_refused()
    result.expect_command_text("12")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_undocked_row_leaves_the_chat_and_cannot_be_undocked_again(story):
    notes = story.agent_creates_task(story.agents.subject, "write the notes")
    story.agent_runs(story.agents.subject, f"task dock {notes}")
    result = story.agent_runs(story.agents.subject, f"task undock {notes}")
    result.expect_command_text(f"Task {notes}: write the notes undocked")
    story.expect_docked_cards()
    result = story.agent_runs(story.agents.subject, f"task {notes} undock")
    result.expect_command_text("is not docked")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_row_docked_again_after_its_card_was_taken_down_shows_again(story):
    notes = story.agent_creates_task(story.agents.subject, "write the notes")
    story.user_docks("tasks", notes)
    card = story.docked_card()
    story.user_did(f"/journal/messages/{card}/unpin", {}, "user unpins the task's card")
    story.clock_ticks(60)
    story.expect_docked_cards()
    story.agent_runs(story.agents.subject, f"task dock {notes}")
    story.expect_docked_cards(f"Task {notes}: write the notes")
    story.expect_stack(story.agents.subject, Ready)
