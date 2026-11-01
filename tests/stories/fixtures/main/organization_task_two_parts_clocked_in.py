from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_task_part_clocked_in import PART_BRIEF, OrganizationTaskPartClockedIn

MAKER_BRIEF = "- the first maker point is met\n- the second maker point is met"


class OrganizationTaskTwoPartsClockedIn(OrganizationTaskPartClockedIn):
    """The Alpha Domain has two Role parts in progress."""

    parent = OrganizationTaskPartClockedIn

    def steps(self, story) -> None:
        domain = story.organization_seat_agent("domain:alpha")
        result = story.agent_runs_as_organization_seat(
            domain, "domain:alpha",
            f'organization part {self.tasks.first} role:alpha/maker "second part" --brief "{MAKER_BRIEF}"',
        )
        result.expect_command_passed()
        self.tasks.second_part = story.newest("tasks")
        self.workers.second = story.newest("workers")
        worker = story.agents.workers.second()
        story.agent_starts_role_session(worker).expect_allowed(worker)
        story.expect_openrig_seat_environment(worker, "role:alpha/maker")
        story.expect_role_job_prompt(worker, MAKER_BRIEF, "old task brief", "journal clock-in")
        story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/maker", "clock-in").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_task(self.tasks.first_part, delegated=True)
        story.expect_task(self.tasks.second_part, delegated=True)
        story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
        story.expect_worker(story.agents.workers.second(), state=WorkerState.READY)
