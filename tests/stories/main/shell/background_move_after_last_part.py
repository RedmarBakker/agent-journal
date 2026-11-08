from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(ShellOptions.MESSAGE_FOREGROUND_LIMIT, 1)
def test_a_long_active_command_moves_with_its_number_and_card(story):
    story.user_sends_message("How is the command going?")
    command = f"python3 -c 'import time; time.sleep({story.setting(ShellOptions.MESSAGE_FOREGROUND_LIMIT) * 4})'"
    output = story.agent_runs_a_command(story.agents.subject, command)
    story.last_step.expect_agent_told(story.agents.subject, ShellNudges.BACKGROUND_MOVE, n=output)
    story.expect_new_output()
    story.expect_run_card_titled(output, "Running python3")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
def test_a_finished_chain_is_not_moved_after_its_last_part(story):
    story.agent_runs_a_command(story.agents.subject, "trap 'sleep 2' EXIT; echo finished")
    story.last_step.expect_shell_text("finished")
    story.last_step.expect_agent_not_told(story.agents.subject, ShellNudges.BACKGROUND_MOVE)
    story.expect_no_new_output()
    story.expect_stack(story.agents.subject, Ready)
