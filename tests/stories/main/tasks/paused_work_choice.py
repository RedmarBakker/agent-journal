from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.paused_work_choice import PausedWorkChoice


@story(PausedWorkChoice, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_resuming_the_paused_task_ends_the_choice(story):
    story.agent_runs(story.agents.subject, f"task resume {story.tasks.started}")
    story.expect_task(story.tasks.started, state=TaskState.STARTED)
    story.expect_task(story.tasks.open, state=TaskState.OPEN)
    story.expect_stack(story.agents.subject, Ready, Working)


@story(PausedWorkChoice, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_skipping_the_paused_task_starts_the_open_one(story):
    story.agent_runs(story.agents.subject, "task skip-paused")
    story.agent_stops(story.agents.subject)
    story.expect_task(story.tasks.open, state=TaskState.STARTED)
    story.expect_task(story.tasks.started, state=TaskState.PAUSED)
    story.expect_stack(story.agents.subject, Ready, Working)
