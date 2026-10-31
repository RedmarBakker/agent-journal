from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_task_split_domain_read import OrganizationTaskSplitDomainRead


PART_BRIEF = "- the part work is met"


class OrganizationTaskPartClockedIn(OrganizationTaskSplitDomainRead):
    """The Alpha Domain has handed its first part to a clocked-in Builder Role."""

    parent = OrganizationTaskSplitDomainRead

    def steps(self, story) -> None:
        domain = story.organization_seat_agent("domain:alpha")
        result = story.agent_runs_as_organization_seat(
            domain, "domain:alpha",
            f'organization part {self.tasks.first} role:alpha/builder "first part" --brief "{PART_BRIEF}"',
        )
        result.expect_command_passed()
        self.tasks.first_part = story.newest("tasks")
        self.workers.first = story.newest("workers")
        worker = story.agents.workers.first()
        story.agent_starts_role_session(worker).expect_allowed(worker)
        story.expect_openrig_seat_environment(worker, "role:alpha/builder")
        story.expect_role_job_prompt(worker, PART_BRIEF, "old task brief", "journal clock-in")
        story.agent_runs_from_openrig_organization_seat(worker, "role:alpha/builder", "clock-in").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_task(self.tasks.first_part, delegated=True)
        story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
