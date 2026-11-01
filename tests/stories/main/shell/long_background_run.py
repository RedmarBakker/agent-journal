from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

CHECK_MINUTES = ShellNudges.BACKGROUND_CHECK.repeat.amount // 60


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_run_in_the_background_past_five_minutes_is_named_at_most_every_five(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "./scripts/migrate.sh")
    result = story.agent_is_quiet_for(story.agents.subject, 1)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    story.time_travel(minutes=CHECK_MINUTES)
    result = story.agent_is_quiet_for(story.agents.subject, 0.1)
    result.expect_agent_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    result = story.agent_is_quiet_for(story.agents.subject, 0.2)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.BACKGROUND_CHECK)
    story.background_run_ends(story.agents.subject, output)
    story.expect_stack(story.agents.subject, Ready)
