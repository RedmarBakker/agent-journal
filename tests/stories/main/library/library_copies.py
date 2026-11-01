from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

COPY = "Review Day (from the library)"


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_library_copy_takes_a_new_version_while_unedited_and_once_edited_waits_for_replace(story):
    original = story.a_library_holds_a_sequence_imported_here("Review Day", "read it")
    copy = story.sequence_number(COPY)
    story.user_types(f"sequence edit {original} --steps 'read it twice'")
    story.user_types(f"library publish sequence {original}")
    result = story.user_types("library update sequence review-day")
    result.expect_command_text("version 2")
    result = story.user_types(f"sequence show {copy}")
    result.expect_command_text("read it twice")
    story.user_types(f"sequence edit {copy} --steps 'my own way'")
    story.user_types(f"sequence edit {original} --steps 'a third way'")
    story.user_types(f"library publish sequence {original}")
    result = story.user_types("library update sequence review-day")
    result.expect_command_refused()
    result.expect_command_text("has edits here to steps: --replace takes")
    story.user_types("library update sequence review-day --replace")
    result = story.user_types(f"sequence show {copy}")
    result.expect_command_text("a third way")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_what_was_imported_keeps_working_once_the_library_is_gone(story):
    story.a_library_holds_a_sequence_imported_here("Tea Time", "brew")
    story.library_server_stops()
    result = story.user_types("library list")
    result.expect_command_text("did not answer")
    result.expect_command_text("journal team connect")
    story.user_types("team disconnect")
    result = story.user_types("sequence list")
    result.expect_command_text("Tea Time (from the library)")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_library_commands_with_no_library_connected_name_the_connect_line(story):
    result = story.user_types("library list")
    result.expect_command_text("journal team connect")
    result = story.user_types("library import sequence x")
    result.expect_command_text("journal team connect")
    result = story.user_types("library publish sequence 1")
    result.expect_command_text("journal team connect")
    story.expect_stack(story.agents.subject, Ready)
