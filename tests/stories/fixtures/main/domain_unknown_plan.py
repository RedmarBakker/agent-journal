from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.domain_delivery_setup import add_domain_plan, setup_domain
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class DomainUnknownPlan(StateFixture):
    """The user composed a task in a domain with no done policy: story.plans.first and story.tasks.first."""

    stack = (Ready,)
    parent = WorkingAgent

    def steps(self, story) -> None:
        setup_domain(story, self, "r02-unknown", "unknown", None)
        add_domain_plan(story, self, "unknown")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, Ready)
