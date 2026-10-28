from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_reading_a_message_the_user_deleted_says_so_and_leaves_nothing_to_do(story):
    message = story.user_sends_message("never mind this")
    story.user_deletes_message(message)
    story.agent_runs(f"message read {message}")
    story.expect_command_text(f"message {message} was deleted by the user; nothing to do")
    story.expect_stack(Ready)
