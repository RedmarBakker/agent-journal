from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

EMAIL, PASSWORD = "ada@example.com", "correct horse battery"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_journal_connects_to_one_library_by_its_password_sees_its_status_logs_in_again_and_disconnects(story):
    library = story.a_library_server_runs()
    result = story.user_types(f"library connect {library} --email {EMAIL}")
    result.expect_command_text("run this line yourself")
    result = story.user_types(f"library connect {library} --email {EMAIL} --name Ada --password '{PASSWORD}'")
    result.expect_command_text("as Ada, admin")
    result = story.user_types("library status")
    result.expect_command_text(f"library {library}, as Ada (admin)")
    result = story.user_types(f"library connect {library} --email {EMAIL} --password x")
    result.expect_command_refused()
    result = story.user_types(f"library login --email {EMAIL} --password '{PASSWORD}'")
    result.expect_command_passed()
    result = story.user_types("library disconnect")
    result.expect_command_text("disconnected")
    result = story.user_types("library status")
    result.expect_command_text("connected to no library")
    story.expect_stack(story.agents.subject, Ready)
