from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.task_queue import TaskQueue

AWAIT = "await 'the build' --until false"
LONG_ENOUGH_MINUTES = 2


def waits_a_while(story) -> None:
    story.agent_runs(story.agents.subject, AWAIT)
    story.time_travel(minutes=LONG_ENOUGH_MINUTES)
    story.agent_reads(story.agents.subject)


@story(TaskQueue, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_paused_task_is_offered_once_at_a_wait_not_at_the_next_waits_with_the_same_task_in_hand_and_again_after_that_task_closes(story):
    story.agent_runs(story.agents.subject, f"task start {story.tasks.open}")
    waits_a_while(story)
    story.expect_agent_told(story.agents.subject, TasksNudges.WAIT_PAUSED_TASK, n=story.tasks.started, count=1)
    story.agent_writes(story.agents.subject, "a.py")
    waits_a_while(story)
    story.expect_agent_told(story.agents.subject, TasksNudges.WAIT_PAUSED_TASK, count=1)
    story.agent_writes(story.agents.subject, "a.py")
    story.agent_runs(story.agents.subject, f"task complete {story.tasks.open}")
    following = story.agent_creates_task(story.agents.subject, "the tests")
    story.agent_runs(story.agents.subject, f"task start {following}")
    waits_a_while(story)
    story.expect_agent_told(story.agents.subject, TasksNudges.WAIT_PAUSED_TASK, count=2)
    story.expect_stack(story.agents.subject, Ready, Working, ExternalWait)
