import shlex

from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
@setting(ShellOptions.MESSAGE_FOREGROUND_LIMIT, 1)
def test_a_background_run_keeps_its_number_and_card_when_its_part_file_was_removed(story):
    story.user_sends_message("How is the command going?")
    child = "import os,time; time.sleep(0.2); os.unlink(os.path.join(os.environ['JOURNAL_OUTPUT_FOLDER'], '0.part'))"
    body = f"import subprocess,time; subprocess.Popen(['python3', '-c', {child!r}]); time.sleep(4)"
    command = f"python3 -c {shlex.quote(body)}"
    output = story.agent_runs_a_command(story.agents.subject, command)
    story.last_step.expect_agent_told(story.agents.subject, ShellNudges.BACKGROUND_MOVE, n=output)
    story.expect_new_output()
    story.expect_run_card_titled(output, "Running python3")
    story.expect_stack(story.agents.subject, Ready)
