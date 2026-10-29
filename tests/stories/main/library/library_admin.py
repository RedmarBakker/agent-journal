from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_withdrawn_item_leaves_the_library_list_while_its_imported_version_still_reads(story):
    original = story.a_library_holds_a_sequence_imported_here("Night Run", "go")
    story.user_types("library withdraw sequence night-run")
    story.user_types("library list")
    story.expect_command_text("no items in the library")
    story.user_types("library show sequence night-run")
    story.expect_command_text("version 1")
    story.user_types(f"library publish sequence {original}")
    story.user_types("library delete sequence night-run 2")
    story.expect_command_text("deleted for good")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_library_admin_invites_with_a_code_and_lists_its_people_and_devices(story):
    story.user_connects_to_a_library()
    story.user_types("library invite bob@example.com")
    story.expect_command_text("code=")
    story.user_types("library people")
    story.expect_command_text("Ada")
    story.user_types("library devices")
    story.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready)
