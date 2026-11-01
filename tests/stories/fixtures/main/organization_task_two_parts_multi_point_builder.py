from journal.engine.states.void import Void
from journal.features.workers.states.working_task import WorkingTask
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.organization_task_split_domain_read import OrganizationTaskSplitDomainRead

BUILDER_BRIEF = "- the first point is met\n- the second point is met"
MAKER_BRIEF = "- the second part is complete"


class OrganizationTaskTwoPartsMultiPointBuilder(OrganizationTaskSplitDomainRead):
    """The Alpha Domain has handed a two-point Builder part and a Maker part to clocked-in Roles."""

    parent = OrganizationTaskSplitDomainRead

    def steps(self, story) -> None:
        domain = story.organization_seat_agent("domain:alpha")
        builder_part = story.agent_runs_as_organization_seat(
            domain, "domain:alpha",
            f'organization part {self.tasks.first} role:alpha/builder "first part" --brief "{BUILDER_BRIEF}"',
        )
        builder_part.expect_command_passed()
        self.tasks.first_part = story.newest("tasks")
        self.workers.first = story.newest("workers")
        builder = story.agents.workers.first()
        story.agent_starts_role_session(builder).expect_allowed(builder)
        story.expect_openrig_seat_environment(builder, "role:alpha/builder")
        story.expect_role_job_prompt(builder, BUILDER_BRIEF, "old task brief", "journal clock-in")
        story.agent_runs_from_openrig_organization_seat(builder, "role:alpha/builder", "clock-in").expect_command_passed()

        maker_part = story.agent_runs_as_organization_seat(
            domain, "domain:alpha",
            f'organization part {self.tasks.first} role:alpha/maker "second part" --brief "{MAKER_BRIEF}"',
        )
        maker_part.expect_command_passed()
        self.tasks.second_part = story.newest("tasks")
        self.workers.second = story.newest("workers")
        maker = story.agents.workers.second()
        story.agent_starts_role_session(maker).expect_allowed(maker)
        story.expect_openrig_seat_environment(maker, "role:alpha/maker")
        story.expect_role_job_prompt(maker, MAKER_BRIEF, "old task brief", "journal clock-in")
        story.agent_runs_from_openrig_organization_seat(maker, "role:alpha/maker", "clock-in").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_task(self.tasks.first_part, delegated=True)
        story.expect_task(self.tasks.second_part, delegated=True)
        story.expect_worker(story.agents.workers.first(), state=WorkerState.READY)
        story.expect_worker(story.agents.workers.second(), state=WorkerState.READY)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
        story.expect_stack(story.agents.workers.second(), Void, WorkingTask)
