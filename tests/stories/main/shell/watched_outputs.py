from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(FOREGROUND_OPTION, 1)
def test_a_watched_output_is_shown_after_a_tool_use_and_not_again_without_new_progress(story):
    output = story.agent_runs_a_command(f"sh -c 'echo 1/3; sleep {story.setting(FOREGROUND_OPTION) * 3}'")
    story.agent_runs(f"output watch {output}")
    story.agent_has_read()
    story.expect_agent_told(ShellNudges.WATCH_VIEW, n=output)
    story.agent_has_read()
    story.expect_agent_not_told(ShellNudges.WATCH_VIEW)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(FOREGROUND_OPTION, 1)
def test_the_end_of_a_watched_output_is_named_as_the_watch_end_alone(story):
    output = story.agent_runs_a_command(f"sh -c 'echo 1/3; sleep {story.setting(FOREGROUND_OPTION) * 2}'")
    story.agent_runs(f"output watch {output}")
    story.background_run_ends(output)
    story.expect_agent_told(ShellNudges.WATCH_ENDED, n=output)
    story.expect_agent_not_told(ShellNudges.OUTPUTS_ENDED)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
@setting(FOREGROUND_OPTION, 1)
def test_an_unwatched_output_is_shown_no_more(story):
    output = story.agent_runs_a_command(f"sh -c 'echo 1/3; sleep {story.setting(FOREGROUND_OPTION) * 3}'")
    story.agent_runs(f"output watch {output}")
    story.agent_runs("output unwatch")
    story.agent_has_read()
    story.expect_agent_not_told(ShellNudges.WATCH_VIEW)
    story.expect_stack(Ready)
