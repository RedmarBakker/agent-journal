from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_task_blocked_until_a_check_opens_when_the_scheduled_check_passes(story):
    waiting = story.agent_creates_task(story.agents.subject, "the deployment")
    blocked = story.agent_runs(story.agents.subject, f"task block {waiting} --until 'exit 0' --every 1")
    blocked.expect_command_passed()
    check = story.newest("checks")
    story.expect_task(waiting, state=TaskState.BLOCKED, waits=[f"checks:{check}"])

    story.scheduled_check_passes(check)

    story.expect_task(waiting, state=TaskState.OPEN, waits=[])
    story.expect_row_absent("checks", check)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_task_in_another_environment_opens_when_its_scheduled_check_passes(story):
    other = story.another_environment("other")
    story.session_starts_in(other, "s-other")
    waiting = story.agent_in_starts_task(story.agents.subject, other, "s-other", "the other deployment")
    blocked = story.agent_in_runs(story.agents.subject, other, "s-other", f"task block {waiting} --until 'exit 0' --every 1")
    blocked.expect_command_passed()
    check = story.newest("checks")
    story.expect_row_in(other, "tasks", waiting, {"state": TaskState.BLOCKED, "waits": [f"checks:{check}"]})

    story.scheduled_check_passes(check)

    story.expect_task_in(other, waiting, TaskState.OPEN)
    story.expect_row_absent("checks", check)
    story.expect_no_faults()
    story.expect_stack(story.agents.subject, Ready)
