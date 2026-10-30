from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.domain_delivery_setup import add_domain_plan, setup_domain
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class DomainPolicyPlan(StateFixture):
    """The user composed a development task under the current done policy: story.plans.first and story.tasks.first."""

    stack = (Ready,)
    parent = WorkingAgent

    def steps(self, story) -> None:
        setup_domain(story, self, "r02-policy-version", "development", {"criterion": "The committed revision is deployed successfully to production.", "evidence": "production_deployment", "target": "production"})
        add_domain_plan(story, self, "development")
        story.user_opens(f"/journal/plans/{self.plans.first}/delivery")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, Ready)
