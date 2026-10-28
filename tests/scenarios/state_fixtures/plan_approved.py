from journal.models.plan_state import PlanState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.builder.stack_states import IDLE
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class PlanApproved(StateFixture):
    """The user made a plan with two tasks, each with a brief a worker can prove, and approved it in the viewer, not yet started: scenario.plan."""

    stack = (IDLE,)

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        scenario.provide(PlanApproved, "plan", scenario.user_creates_plan("p", "b"))
        scenario.user_adds_plan_task(scenario.plan, "first", "- writes part one")
        scenario.user_adds_plan_task(scenario.plan, "second", "- writes part two")
        scenario.user_approves_plan(scenario.plan)

    def expected(self, scenario) -> None:
        scenario.expect_plan(scenario.plan, state=PlanState.APPROVED)
