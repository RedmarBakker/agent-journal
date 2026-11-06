from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.passed_wait_check import PassedWaitCheck
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(PassedWaitCheck, subject=AgentRole.MAIN)
def test_a_passed_wait_line_is_not_sent_again_at_the_stop(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.WAIT_CHECK_PASSED, what="the nightly build", lines="the check passed")
    story.expect_stack(story.agents.subject, Ready)


@story(PassedWaitCheck, subject=AgentRole.MAIN)
def test_two_checks_with_the_same_purpose_do_not_repeat_the_same_pass_line(story):
    story.agent_runs(story.agents.subject, "await 'the nightly build' --until 'exit 0'")
    second = story.newest("checks")
    second_result = story.agent_runs(story.agents.subject, f"check run {second}")
    second_result.expect_agent_told_count(story.agents.subject, TasksNudges.WAIT_CHECK_PASSED, 0, what="the nightly build", lines="the check passed")
    second_result.expect_agent_told_count(story.agents.subject, TasksNudges.WAIT_END, 1)
    result = story.agent_stops(story.agents.subject)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.WAIT_END)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_cleared_await_removes_its_check(story):
    story.agent_runs(story.agents.subject, "await 'the second build' --until 'exit 0'")
    check = story.newest("checks")
    result = story.agent_runs(story.agents.subject, "await clear")
    result.expect_command_text(f"check {check} removed")
    story.expect_stack(story.agents.subject, Ready)
