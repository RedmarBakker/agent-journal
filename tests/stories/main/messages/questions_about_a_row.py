from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_message_asked_about_a_docked_run_names_its_row_to_the_agent_and_a_row_not_there_is_refused(story):
    story.agent_runs(story.agents.subject, "check create 'the suite' --command true --brief 'the suite passes'")
    check = story.created_number("check")
    story.user_asks_about([f"checks:{check}"], "> Check the suite failed\n\nwhy did it fail?")
    asked = story.newest("messages")
    story.agent_runs(story.agents.subject, f"message read {asked}")
    story.expect_command_text(f"refers_to checks:{check}")
    story.user_asks_about(["checks:999"], "x")
    story.expect_viewer_refused("")
    story.expect_stack(story.agents.subject, Ready)
