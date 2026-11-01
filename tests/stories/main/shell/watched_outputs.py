from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_watched_output_is_shown_after_a_tool_use_until_its_end_is_named_as_the_watch_end_alone(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "./scripts/migrate.sh", "1/3")
    result = story.agent_runs(story.agents.subject, f"output watch {output} --title src/app.py")
    result.expect_command_refused()
    story.agent_runs(story.agents.subject, f"output watch {output}")
    result = story.agent_has_read(story.agents.subject)
    result.expect_agent_told(story.agents.subject, ShellNudges.WATCH_VIEW, n=output)
    result = story.agent_has_read(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.WATCH_VIEW)
    result = story.background_run_ends(story.agents.subject, output)
    result.expect_agent_told(story.agents.subject, ShellNudges.WATCH_ENDED, n=output)
    result.expect_agent_not_told(story.agents.subject, ShellNudges.OUTPUTS_ENDED)
    story.expect_stack(story.agents.subject, Ready)
