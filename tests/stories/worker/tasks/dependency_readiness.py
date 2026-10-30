from journal.engine.states.void import Void
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.dependency_plan_worker import DependencyPlanWorker


@story(DependencyPlanWorker, mode=BUILDER_MODE, subject=AgentRole.WORKER)
def test_a_worker_keeps_its_current_task_when_a_dependent_task_is_refused(story):
    result = story.agent_runs(story.agents.subject, f"task start {story.tasks.second}")
    result.expect_command_refused()
    result.expect_command_text(f"task {story.tasks.first}")
    story.expect_task(story.tasks.first, state=TaskState.STARTED, delegated=True)
    story.expect_task(story.tasks.second, state=TaskState.OPEN, delegated=False)
    story.expect_worker(story.agents.subject, state=WorkerState.READY)
    story.expect_stack(story.agents.subject, Void, WorkingTask)
