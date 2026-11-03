from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.organization_shared_role_task_clocked_in import OrganizationSharedRoleTaskClockedIn


@story(OrganizationSharedRoleTaskClockedIn, subject=AgentRole.MAIN)
def test_a_live_codex_worker_is_not_ended_when_a_role_seat_has_its_pid(story):
    worker = story.codex_worker_runs_as_a_live_process_sharing_a_role_pid(story.agents.workers.first())
    story.expect_worker(worker, state=WorkerState.DISPATCHED)
    story.expect_stack(story.agents.subject)
