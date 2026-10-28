from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

EMAIL, PASSWORD = "ada@example.com", "correct horse battery"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_journal_connects_to_one_library_by_its_password_sees_its_status_logs_in_again_and_disconnects(story):
    library = story.a_library_server_runs()
    story.user_types(f"library connect {library} --email {EMAIL}")
    story.expect_command_text("run this line yourself")
    story.user_types(f"library connect {library} --email {EMAIL} --name Ada --password '{PASSWORD}'")
    story.expect_command_text("as Ada, admin")
    story.user_types("library status")
    story.expect_command_text(f"library {library}, as Ada (admin)")
    story.user_types(f"library connect {library} --email {EMAIL} --password x")
    story.expect_command_refused()
    story.user_types(f"library login --email {EMAIL} --password '{PASSWORD}'")
    story.expect_command_passed()
    story.user_types("library disconnect")
    story.expect_command_text("disconnected")
    story.user_types("library status")
    story.expect_command_text("connected to no library")
    story.expect_stack(Ready)
