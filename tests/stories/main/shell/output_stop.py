from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_agent_stops_a_run_it_waits_on_and_the_run_ends_failed_with_the_wait(story):
    output = story.agent_has_a_background_run_printing(story.agents.subject, "kubectl delete pv stuck-volume")
    story.agent_runs(story.agents.subject, f"await 'the volume delete' --output {output}")
    result = story.agent_runs(story.agents.subject, f"output stop {output}")
    result.expect_command_passed()
    result.expect_command_text(f"output {output} stopped")
    result = story.agent_runs(story.agents.subject, f"output status {output}")
    result.expect_command_text("failed with code 137")
    result = story.agent_runs(story.agents.subject, f"output stop {output}")
    result.expect_command_refused()
    result.expect_command_text("ended already")
    story.expect_stack(story.agents.subject, Ready)
