from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_domain_role_task import OrganizationDomainRoleTask


@story(OrganizationDomainRoleTask, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_role_seat_keeps_its_clocked_in_job_when_its_hook_session_changes(story):
    task = story.tasks.second
    handed_to_role = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} role:alpha/builder",
    )
    handed_to_role.expect_command_passed()
    worker_number = story.newest("workers")
    story.fixture.workers.first = worker_number
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, "- task 6 has its current brief", "- first is done")

    started = story.agent_starts_role_session(worker)
    started.expect_allowed(worker)
    clocked_in = story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in")
    clocked_in.expect_command_passed()
    story.expect_stack(worker, Void, WorkingTask)

    restarted = story.role_seat_starts_a_new_session(worker, "role:alpha/builder")
    restarted.expect_allowed(worker)
    story.expect_stack(worker, Void, WorkingTask)
    read = story.agent_reads_from_organization_role_seat(worker, "role:alpha/builder", "source/NOTES.md")
    read.expect_allowed()
    edited = story.agent_writes_from_organization_role_seat(worker, "role:alpha/builder", "source/NOTES.md")
    edited.expect_allowed()

    story.agent_proves(worker, 1, "the current task brief is met: task 6 has its current brief")
    story.agent_clocks_out(worker, "the task brief is met")
    checked = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"worker check {worker} 1",
    )
    checked.expect_command_passed()
    returned = story.agent_runs_from_organization_seat(
        story.agents.main, "domain:alpha", f"organization handoff {task} plan",
    )
    returned.expect_command_passed()
    plan_inbox = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", "organization inbox")
    plan_inbox.expect_command_passed()
    merged = story.agent_runs_from_plan_organization_seat(story.agents.main, "plan", f"worker merge {worker}")
    merged.expect_command_passed()

    story.expect_task(task, state=TaskState.COMPLETED)
    story.expect_worker(worker, state=WorkerState.MERGED)
    story.expect_plan(story.plans.first, state=PlanState.FINISHED)
    story.expect_organization_seat_routing_guidance(f"plan-{story.plans.first}")
    story.expect_stack(worker, Void)
