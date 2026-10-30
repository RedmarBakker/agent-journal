from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_published_sequence_is_imported_once_as_an_editable_copy_and_a_second_publish_is_its_version_two(story):
    story.user_connects_to_a_library()
    story.user_types("sequence create 'Ship Week' --steps 'tag it | push it'")
    sequence = story.created_number("sequence")
    story.user_types(f"library publish sequence {sequence} --note first")
    result = story.user_types("library import sequence ship-week")
    result.expect_command_text("version 1")
    result = story.user_types("sequence list")
    result.expect_command_text("Ship Week (from the library)")
    result = story.user_types("library import sequence ship-week")
    result.expect_command_text("imported already")
    result = story.user_types(f"library publish sequence {sequence} --note second")
    result.expect_command_text("version 2")
    result = story.user_types("library list")
    result.expect_command_text("sequence ship-week: version 2, you have 1")
    result = story.user_types("library publish template nine")
    result.expect_command_refused()
    story.expect_stack(story.agents.subject, Ready)
