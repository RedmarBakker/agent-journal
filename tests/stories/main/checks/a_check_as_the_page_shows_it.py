from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

TITLE, BRIEF, COMMAND = "Check for sins", "Judges the project; a failure lists the sins found", "true"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_an_edited_check_shows_what_the_edit_names_and_no_run_yet_and_runs_its_new_command(story):
    story.agent_runs(f"check create '{TITLE}' --command 'false' --brief 'fails'")
    check = story.created_number("check")
    story.agent_runs(f"check edit {check} --command '{COMMAND}' --brief '{BRIEF}' --every 5")
    story.expect_row("checks", check, {"title": TITLE, "command": COMMAND, "brief": BRIEF, "last_run_at": None})
    story.agent_runs(f"check run {check}")
    story.expect_command_passed()
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_check_run_that_fails_is_told_to_the_page_as_a_change_of_its_row(story):
    story.agent_runs("check create 'Fails' --command 'false' --brief 'always fails'")
    check = story.created_number("check")
    story.agent_runs(f"check run {check}")
    story.expect_change_told_to_the_viewer("checks", check)
    story.expect_stack(Ready)
