from journal.features.shell.shell_options import ShellOptions
from journal.features.shell.support.output_view import OutputView
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
@setting(ShellOptions.OUTPUT_DOCK, False)
def test_an_awaited_run_is_docked_from_the_start_of_the_wait_and_cannot_be_taken_down_until_it_ends(story):
    output = story.agent_runs_a_command(f"sleep {story.setting(FOREGROUND_OPTION) * 4}")
    story.agent_runs(f"await 'the long sleep' --output {output}")
    card = story.card_number(OutputView.key(output))
    story.expect_card_data(card, docked=True, waiting_run=True)
    story.user_presses(f"/journal/messages/{card}/undock", {})
    story.expect_viewer_refused("stays docked while the agent waits for it")
    story.background_run_ends(output)
    story.expect_card_data(card, waiting_run=False)
    story.user_presses(f"/journal/messages/{card}/undock", {})
    story.expect_viewer_passed()
    story.expect_card_data(card, docked=False)
    story.expect_stack(Ready)
