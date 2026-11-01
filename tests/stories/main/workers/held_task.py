from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(WorkerDelivered, subject=AgentRole.MAIN)
def test_a_task_a_worker_holds_is_started_by_no_agent_until_the_worker_lets_it_go(story):
    result = story.agent_runs(story.agents.subject, f"task start {story.tasks.briefed}")
    result.expect_command_refused()
    result.expect_command_text(
        f"task {story.tasks.briefed} is held by worker {story.agents.workers.first()}: "
        f"release it with `journal worker release {story.agents.workers.first()}`",
    )
    story.agent_runs(story.agents.subject, f"worker release {story.agents.workers.first()} --drop")
    result = story.agent_runs(story.agents.subject, f"task start {story.tasks.briefed}")
    result.expect_command_passed()
    story.expect_task(story.tasks.briefed, state=TaskState.STARTED)
    story.expect_stack(story.agents.subject, Ready, Working)
