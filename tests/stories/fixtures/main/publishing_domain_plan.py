from pathlib import Path

from journal.features.tasks.states.ready import Ready
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PublishingDomainPlan(StateFixture):
    """The user's draft plan belongs to a publishing domain with owner-attested delivery evidence in its contract."""

    parent = UserDraftedPlan
    settings = ((OrganizationOptions.FOLDER, str(Path(__file__).with_name("publishing_organization"))),)

    def steps(self, story) -> None:
        pass

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_task(self.tasks.second, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, Ready)
