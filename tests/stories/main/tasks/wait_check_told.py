from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_wait_lifted_by_working_tells_the_agent_once_when_its_check_passes(story):
    story.agent_runs(story.agents.subject, "await 'the nightly build' --until 'exit 0'")
    check = story.newest("checks")
    result = story.agent_reads(story.agents.subject)
    result.expect_agent_told(story.agents.subject, TasksNudges.WAIT_LIFTED, what="the nightly build", n=check)
    result = story.agent_runs(story.agents.subject, f"check run {check}")
    result.expect_agent_told(story.agents.subject, TasksNudges.WAIT_CHECK_PASSED, what="the nightly build")
    story.expect_row_absent("checks", check)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_cleared_await_removes_its_check(story):
    story.agent_runs(story.agents.subject, "await 'the second build' --until 'exit 0'")
    check = story.newest("checks")
    result = story.agent_runs(story.agents.subject, "await clear")
    result.expect_command_text(f"check {check} removed")
    story.expect_stack(story.agents.subject, Ready)
