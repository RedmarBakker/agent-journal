from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.worker.plan_worker import PlanWorker
from tests.stories.fixtures.worker.plan_worker_delivered import PlanWorkerDelivered


@story(PlanWorkerDelivered, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_each_task_checked_and_the_worker_merged_finishes_the_plan(story):
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 1 --task {story.tasks.first}")
    story.agent_runs(story.agents.subject, f"worker check {story.agents.workers.first()} 1 --task {story.tasks.second}")
    result = story.agent_runs(story.agents.subject, f"worker merge {story.agents.workers.first()}")
    result.expect_command_passed()
    story.expect_worker(story.agents.workers.first(), state=WorkerState.MERGED)
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)
    result.expect_agent_told(story.agents.subject, WorkersNudges.IDLE_WORKER, n=story.agents.workers.first())
    story.expect_stack(story.agents.subject, Ready)


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_dispatched_with_a_report_choice_is_refused_since_every_worker_reports_once_no_task_is_left(story):
    result = story.agent_runs(story.agents.subject, f"worker dispatch 'Lady Lovelace' --plan {story.plans.first} --changes 'the files of its tasks' --profile journal-medior --model sonnet --tests 'Scoped tests' --report each")
    result.expect_command_refused()
    result.expect_command_text("--report")
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_queued_task_the_user_cancels_leaves_the_queue(story):
    story.user_cancels_task(story.tasks.second, "not needed")
    story.agent_proves(story.agents.workers.first(), 1, "first.py:3, test_first passes")
    result = story.agent_clocks_out(story.agents.workers.first(), "the first is done")
    result.expect_agent_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.DELIVERED)
    story.expect_task(story.tasks.second, state=TaskState.CANCELLED)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_queued_task_that_is_blocked_ends_the_queue_with_a_report(story):
    story.agent_runs(story.agents.subject, f"task block {story.tasks.second} 'waits on the designer'")
    story.agent_proves(story.agents.workers.first(), 1, "first.py:3, test_first passes")
    result = story.agent_clocks_out(story.agents.workers.first(), "the first is done")
    result.expect_agent_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_task(story.tasks.second, state=TaskState.BLOCKED)
    story.expect_task(story.tasks.first, delegated=True)
    story.expect_stack(story.agents.subject, Ready)


@story(PlanWorker, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_worker_goes_on_to_the_next_task_as_it_proves_the_last_point_and_the_plan_shows_the_proved_one_waiting_for_the_check(story):
    result = story.agent_proves(story.agents.workers.first(), 1, "first.py:3, test_first passes")
    result.expect_agent_not_told(story.agents.subject, WorkersNudges.WORK_READY)
    story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
    story.expect_task(story.tasks.second, delegated=True)
    result = story.agent_runs(story.agents.subject, f"plan show {story.plans.first}")
    result.expect_command_text(f"{story.tasks.first:>4}  proved")
    result.expect_command_text("finished by its worker, waiting for your check")
    result = story.user_opens(f"/journal/plans?ids={story.plans.first}")
    result.expect_viewer_part(("rows", 0, "proved_task_ids"), [story.tasks.first])
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
