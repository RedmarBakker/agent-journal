from pathlib import Path

from journal.features.organization.support.organization import Organization
from journal.features.workers.organization_options import OrganizationOptions
from tests.stories.fixtures.main.organization_plan_without_domain_seats import OrganizationPlanWithoutDomainSeats


class OrganizationTaskSplitPlan(OrganizationPlanWithoutDomainSeats):
    """An organization plan uses two writing Roles for task parts."""

    parent = OrganizationPlanWithoutDomainSeats
    settings = (
        (OrganizationOptions.FOLDER, str(Path(__file__).resolve().with_name("organization_task_split"))),
    )

    def steps(self, story) -> None:
        story.app.container.get(Organization).reload()
        listed = story.agent_runs(story.agents.main, "organization list")
        listed.expect_command_passed()
        listed.expect_command_text("builder")
        listed.expect_command_text("maker")
