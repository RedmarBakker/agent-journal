from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

TITLE, BRIEF, COMMAND = "Check for sins", "Judges the project; a failure lists the sins found", "true"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_new_check_shows_its_title_its_description_and_its_command_and_no_run_yet(story):
    story.agent_runs(f"check create '{TITLE}' --command '{COMMAND}' --brief '{BRIEF}'")
    story.expect_command_passed()
    story.expect_row("checks", story.created_number("check"), {"title": TITLE, "brief": BRIEF, "command": COMMAND, "last_run_at": None})
    story.expect_stack(Ready)
