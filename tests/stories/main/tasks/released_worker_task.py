from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.released_worker_task_in_hand import ReleasedWorkerTaskInHand


@story(ReleasedWorkerTaskInHand, subject=AgentRole.MAIN)
def test_a_blocked_task_from_a_released_worker_does_not_hold_the_main_agent(story):
    task = story.tasks.briefed
    other = story.agent_creates_briefed_task(story.agents.subject, "the footer", "write the footer")
    started = story.agent_runs(story.agents.subject, f"task start {other}")
    started.expect_command_passed()
    story.expect_task(task, state=TaskState.BLOCKED, delegated=False)
    story.expect_task(other, state=TaskState.STARTED, delegated=False)
    story.expect_stack(story.agents.subject, Ready, Working)
