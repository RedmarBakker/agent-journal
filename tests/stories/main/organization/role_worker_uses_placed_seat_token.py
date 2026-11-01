from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.features.organization.support.rig_staffing import RigStaffing
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_shared_role_seat_placed import OrganizationSharedRoleSeatPlaced


@story(OrganizationSharedRoleSeatPlaced, subject=AgentRole.MAIN)
def test_a_role_worker_uses_the_token_placed_before_its_worker_row(story):
    task = story.tasks.first
    plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
    staffing = story.app.container.get(RigStaffing)
    runtime = story.app.container.get(SeatRuntime)
    shared_rig = staffing.shared_rig_name(plan.environment_id)
    placed = runtime.organization_member(shared_rig, "role:alpha/shared", story.provider)
    seat_token = placed.token
    story.expect_row_count("workers", 0)

    domain = story.organization_seat_agent("domain:alpha")
    handed = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/shared",
    )
    handed.expect_command_passed()

    story.fixture.workers.first = story.newest("workers")
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, "the current brief is met", "an earlier task brief")
    story.expect_worker_uses_relaunched_seat_token(worker, seat_token)
    story.expect_openrig_seat_environment(worker, "role:alpha/shared", shared_rig)
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/shared", "clock-in", shared_rig,
    ).expect_command_passed()
    story.agent_reads_from_organization_role_seat(
        worker, "role:alpha/shared", "source/NOTES.md",
    ).expect_allowed(worker)
    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_worker_uses_relaunched_seat_token(worker, seat_token)
    story.expect_stack(worker, Void, WorkingTask)
