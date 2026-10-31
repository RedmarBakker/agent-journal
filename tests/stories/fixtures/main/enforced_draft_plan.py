from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.skills.feature import Skills
from journal.features.tasks.states.ready import Ready
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.plan_state import PlanState
from tests.organization_fixture import OrganizationFixture
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class EnforcedDraftPlan(StateFixture):
    """The user enabled estimates enforcement, configured development delivery criteria and created a plan for the agent to compose."""

    stack = (Ready,)
    parent = WorkingAgent

    def steps(self, story) -> None:
        folder = story.app.config.root / "w02-enforced"
        organization = OrganizationFixture(folder).write()
        organization.domain("development", roles=["delivery"], definition_of_done={
            "criterion": "The committed revision is deployed successfully to production.",
            "evidence": "production_deployment",
            "target": "production",
        })
        organization.role("development", "delivery", writes=True, tools=["read_files", "edit_files"])
        story.user_sets(OrganizationOptions.FOLDER, str(folder))
        story.user_presses("/journal/organization/reload", {}).expect_viewer_passed()
        story.user_sets(EstimatesOptions.MODE, "enforce")
        story.user_switches_on(Skills)
        self.plans.first = story.user_creates_plan("the delivery", "production receives the revision")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_stack(story.agents.main, Ready)
