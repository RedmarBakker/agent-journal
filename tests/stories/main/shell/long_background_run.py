from pathlib import Path

from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.repositories.command_outputs import CommandOutputs
from journal.support.agent_role import AgentRole
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.heartbeat import Heartbeat
from journal.support.time_source import TimeSource
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

CHECK_MINUTES = ShellNudges.BACKGROUND_CHECK.repeat.amount // 60


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
def test_a_run_in_the_background_past_five_minutes_is_named_at_most_every_five(story):
    output = story.agent_runs_a_command(story.agents.subject, f"sh -c 'sleep {story.setting(FOREGROUND_OPTION) * 4}'")
    run = story.app.container.get(CommandOutputs).find(output)
    Heartbeat(Path(run.folder)).write(story.app.container.get(TimeSource).seconds() + CHECK_MINUTES * 60)
    result = story.agent_is_quiet_for(story.agents.subject, 0.1)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    story.time_travel(minutes=CHECK_MINUTES)
    result = story.agent_is_quiet_for(story.agents.subject, 0.1)
    result.expect_agent_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    result = story.agent_is_quiet_for(story.agents.subject, 0.2)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    story.background_run_ends(output)
    story.expect_stack(story.agents.subject, Ready)
