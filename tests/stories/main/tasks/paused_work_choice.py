from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_work_choice import PausedWorkChoice


@story(PausedWorkChoice, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_resuming_the_paused_task_ends_the_choice(story):
    story.agent_runs(f"task resume {story.start.started_task}")
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_task(story.start.next_open, state=TaskState.OPEN)
    story.expect_stack(Ready, Working)


@story(PausedWorkChoice, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_skipping_the_paused_task_starts_the_open_one(story):
    story.agent_runs("task skip-paused")
    story.agent_stops()
    story.expect_task(story.start.next_open, state=TaskState.STARTED)
    story.expect_task(story.start.started_task, state=TaskState.PAUSED)
    story.expect_stack(Ready, Working)
