from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
@setting(ShellOptions.UNREAD_OUTPUT_INTERVAL, 2)
def test_an_ended_run_left_unread_is_named_again_after_the_set_tool_uses(story):
    output = story.agent_runs_a_command(f"sleep {story.setting(FOREGROUND_OPTION) * 2}")
    story.background_run_ends(output)
    for _ in range(story.setting(ShellOptions.UNREAD_OUTPUT_INTERVAL)):
        story.agent_reads()
        story.agent_has_read()
    story.expect_agent_told(ShellNudges.UNREAD_OUTPUT, n=output)
    story.expect_stack(Ready)
