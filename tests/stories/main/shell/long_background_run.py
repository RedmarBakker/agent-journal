from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.builder.story_marks import setting, story
from tests.stories.fixtures.main.working_agent import WorkingAgent

CHECK_MINUTES = ShellNudges.BACKGROUND_CHECK.repeat.amount // 60


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(FOREGROUND_OPTION, 1)
def test_a_run_in_the_background_past_five_minutes_is_named_at_most_every_five(story):
    output = story.agent_runs_a_command(story.agents.subject, f"sh -c 'sleep {story.setting(FOREGROUND_OPTION) * 4}'")
    story.agent_is_quiet_for(story.agents.subject, 1)
    story.expect_agent_not_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    story.agent_is_quiet_for(story.agents.subject, CHECK_MINUTES + 1)
    story.expect_agent_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    story.agent_is_quiet_for(story.agents.subject, CHECK_MINUTES + 2)
    story.expect_agent_not_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    story.background_run_ends(output)
    story.expect_stack(story.agents.subject, Ready)
