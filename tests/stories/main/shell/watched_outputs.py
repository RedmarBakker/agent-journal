from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
def test_a_watched_output_is_shown_after_a_tool_use_until_its_end_is_named_as_the_watch_end_alone(story):
    output = story.agent_runs_a_command(f"sh -c 'echo 1/3; sleep {story.setting(FOREGROUND_OPTION) * 3}'")
    story.agent_runs(f"output watch {output} --title src/app.py")
    story.expect_command_refused()
    story.agent_runs(f"output watch {output}")
    story.agent_has_read()
    story.expect_agent_told(ShellNudges.WATCH_VIEW, n=output)
    story.agent_has_read()
    story.expect_agent_not_told(ShellNudges.WATCH_VIEW)
    story.background_run_ends(output)
    story.expect_agent_told(ShellNudges.WATCH_ENDED, n=output)
    story.expect_agent_not_told(ShellNudges.OUTPUTS_ENDED)
    story.expect_stack(Ready)
