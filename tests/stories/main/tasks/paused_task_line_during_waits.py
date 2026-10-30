from journal.features.tasks.states.external_wait import NEXT_TASK_DELAY, ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.task_queue import TaskQueue

AWAIT = "await 'the build' --until false"


def waits_a_minute(story) -> None:
    story.agent_runs(story.agents.subject, AWAIT)
    story.agent_is_quiet_past(story.agents.subject, NEXT_TASK_DELAY.amount)


@story(TaskQueue, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_paused_task_is_offered_once_at_a_wait_not_at_the_next_waits_with_the_same_task_in_hand_and_again_after_that_task_closes(story):
    story.agent_runs(story.agents.subject, f"task start {story.tasks.open}")
    waits_a_minute(story)
    story.expect_typed_nudge(TasksNudges.WAIT_PAUSED_TASK, count=1, n=story.tasks.started, what="the build")
    story.agent_writes(story.agents.subject, "a.py")
    waits_a_minute(story)
    story.expect_typed_nudge(TasksNudges.WAIT_PAUSED_TASK, count=1, n=story.tasks.started, what="the build")
    story.agent_writes(story.agents.subject, "a.py")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.open}")
    following = story.agent_creates_task(story.agents.subject, "the tests")
    story.agent_runs(story.agents.subject, f"task start {following}")
    story.agent_runs(story.agents.subject, AWAIT)
    story.expect_stack(story.agents.subject, Ready)
    waits_a_minute(story)
    story.expect_typed_nudge(TasksNudges.WAIT_PAUSED_TASK, count=2, n=story.tasks.started, what="the build")
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)
