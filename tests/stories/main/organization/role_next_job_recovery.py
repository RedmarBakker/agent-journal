from journal.engine.states.void import Void
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.workers.states.working_task import WorkingTask
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_role_worker_ended import OrganizationRoleWorkerEnded
from tests.stories.fixtures.main.shared_role_queue import awaiting_state


@story(OrganizationRoleWorkerEnded, subject=AgentRole.MAIN)
def test_a_role_with_an_ended_run_restarts_before_its_next_queued_task(story):
    plan, current_task = story.plans.first, story.tasks.second
    next_task = story.user_adds_plan_task(plan, "the next Role task", "alpha")
    worker = story.agents.workers.first()
    domain = story.organization_seat_agent("domain:alpha")

    handoff = story.agent_runs_as_organization_seat(
        domain, "domain:alpha", f"organization handoff {next_task} role:alpha/builder",
    )
    handoff.expect_command_passed()
    handoff.expect_command_text(f"task {next_task} routed from domain:alpha to role:alpha/builder")
    handoff.expect_command_text(f"worker {worker} Builder task {current_task} queue: task {next_task}")

    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_worker_role_job(worker, current_task, "- task 6 has its current brief", "- first is done")
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.expect_role_job_prompt(
        worker, "- task 6 has its current brief", "- first is done", "journal clock-in",
    )
    story.agent_clocks_in(worker).expect_command_passed()

    story.expect_task(current_task, state=TaskState.STARTED, delegated=True)
    story.expect_task(next_task, state=TaskState.OPEN, delegated=True)
    story.expect_worker(worker, state=WorkerState.READY)
    story.expect_stack(worker, Void, WorkingTask)
    story.expect_stack(story.agents.subject, LeadingPlan, FollowingPlan, awaiting_state(story))
