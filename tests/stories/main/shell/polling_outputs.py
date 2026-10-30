from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_conduct import POLL_REPEAT_COMMANDS
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_third_poll_in_a_row_of_the_same_output_is_refused_with_the_await(story):
    output = story.agent_runs_a_command(story.agents.subject, "echo hi | head -1")
    story.agent_runs_in_the_shell(story.agents.subject, f"journal output status {output}")
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal output status {output}")
    result.expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, f"journal output status {output}")
    result.expect_refused(story.agents.subject, TasksNudges.OUTPUT_POLL_REFUSAL, n=output)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_same_command_run_again_and_again_is_named(story):
    for _ in range(POLL_REPEAT_COMMANDS):
        story.agent_runs_in_the_shell(story.agents.subject, "git status")
    story.last_step.expect_agent_told(story.agents.subject, TasksNudges.STOP_POLLING, times=POLL_REPEAT_COMMANDS, command="git status")
    story.expect_stack(story.agents.subject, Ready)
