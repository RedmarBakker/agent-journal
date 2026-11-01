from journal.features.shell.shell_options import ShellOptions
from journal.features.shell.support.output_view import OutputView
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(ShellOptions.OUTPUT_DOCK, False)
def test_an_awaited_run_is_docked_from_the_start_of_the_wait_and_cannot_be_taken_down_until_it_ends(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "sleep 4")
    story.agent_runs(story.agents.subject, f"await 'the long sleep' --output {output}")
    card = story.card_number(OutputView.key(output))
    story.expect_card_data(card, docked=True, waiting_run=True)
    result = story.user_presses(f"/journal/messages/{card}/undock", {})
    result.expect_viewer_refused("stays docked while the agent waits for it")
    story.background_run_ends(story.agents.subject, output)
    story.expect_card_data(card, waiting_run=False)
    result = story.user_presses(f"/journal/messages/{card}/undock", {})
    result.expect_viewer_passed()
    story.expect_card_data(card, docked=False)
    story.expect_stack(story.agents.subject, Ready)
