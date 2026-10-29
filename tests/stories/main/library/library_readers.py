from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PATTERN = "error:"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reader_published_to_the_library_is_imported_only_once_its_pattern_is_read_and_accepted(story):
    story.user_connects_to_a_library()
    story.user_types(f"reader add errors --pattern '{PATTERN}' --about 'the errors a run prints'")
    story.user_types("library publish reader errors --note first")
    story.expect_command_passed()
    story.user_types("reader remove errors")
    story.user_types("library import reader errors")
    story.expect_command_refused()
    story.expect_command_text(PATTERN)
    story.user_types("reader list")
    story.expect_command_text_without("errors")
    story.user_types("library import reader errors --accept")
    story.expect_command_passed()
    story.user_types("reader list")
    story.expect_command_text("errors")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_reader_from_the_library_never_overwrites_a_reader_file_this_journal_has(story):
    story.user_types(f"reader add errors --pattern '{PATTERN}' --about 'the errors a run prints'")
    story.user_connects_to_a_library()
    story.user_types("library publish reader errors")
    story.user_types("library import reader errors --accept")
    story.expect_command_refused()
    story.expect_command_text("exists here already")
    story.expect_stack(story.agents.subject, Ready)
