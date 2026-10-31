from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.worker.queued_worker import QueuedWorker
from tests.stories.fixtures.worker.worker_delivered import WorkerDelivered


@story(WorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_dispatch_refusal_for_a_worker_held_task_names_its_release_command(story):
    task = story.tasks.briefed
    worker = story.agents.workers.first()
    result = story.agent_runs(
        story.agents.subject,
        f"worker dispatch 'Grace Hopper' --task {task} --changes 'the parser' --profile journal-medior --model sonnet",
    )
    result.expect_command_refused()
    result.expect_command_text(f"task {task} is held by worker {worker}: release it with `journal worker release {worker}`")
    story.expect_task(task, delegated=True)
    story.expect_stack(story.agents.subject, Ready)


@story(QueuedWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_dispatch_refusal_for_a_queued_task_names_the_drain_command(story):
    task = story.tasks.queued
    worker = story.agents.workers.first()
    result = story.agent_runs(
        story.agents.subject,
        f"worker dispatch 'Grace Hopper' --task {task} --changes 'the docs' --profile journal-medior --model sonnet",
    )
    result.expect_command_refused()
    result.expect_command_text(f"task {task} is queued for worker {worker}: remove it with `journal worker drain {worker}`")
    story.expect_task(task, delegated=True)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
