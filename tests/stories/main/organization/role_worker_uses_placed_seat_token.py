from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_shared_role_seat_placed import OrganizationSharedRoleSeatPlaced


@story(OrganizationSharedRoleSeatPlaced, subject=AgentRole.MAIN)
def test_a_role_worker_uses_the_token_placed_before_its_worker_row(story):
    task = story.tasks.first
    seat_token = story.fixture.seat_token
    shared_rig = story.fixture.shared_rig
    story.expect_row_count("workers", 0)

    domain = story.organization_seat_agent("domain:alpha")
    handed = story.agent_runs_from_openrig_organization_seat(
        domain, "domain:alpha", f"organization handoff {task} role:alpha/shared",
    )
    handed.expect_command_passed()

    story.fixture.workers.first = story.newest("workers")
    worker = story.agents.workers.first()
    story.expect_worker_role_job(worker, task, "the current brief is met", "an earlier task brief")
    story.expect_worker_token(worker, seat_token)
    story.expect_openrig_seat_environment(worker, "role:alpha/shared", shared_rig)
    story.agent_starts_role_session(worker).expect_allowed(worker)
    story.agent_runs_from_openrig_organization_seat(
        worker, "role:alpha/shared", "clock-in", shared_rig,
    ).expect_command_passed()
    story.agent_reads_from_organization_role_seat(
        worker, "role:alpha/shared", "source/NOTES.md",
    ).expect_allowed(worker)
    story.expect_task(task, state=TaskState.STARTED, delegated=True)
    story.expect_worker_token(worker, seat_token)
    story.expect_stack(worker, Void, WorkingTask)
