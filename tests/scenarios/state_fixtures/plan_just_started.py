from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.builder.stack_states import FOLLOWING_PLAN, IDLE
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class PlanJustStarted(StateFixture):
    """The user made a plan with one task and approved it in the viewer, and the agent at work started it, so its task is in hand: scenario.plan and scenario.task_in_hand."""

    stack = (IDLE, FOLLOWING_PLAN)

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        scenario.provide(PlanJustStarted, "plan", scenario.user_creates_plan("p", "b"))
        scenario.provide(PlanJustStarted, "task_in_hand", scenario.user_adds_plan_task(scenario.plan, "first"))
        scenario.user_approves_plan(scenario.plan)
        scenario.agent_runs(f"plan start {scenario.plan}")

    def expected(self, scenario) -> None:
        scenario.expect_plan(scenario.plan, state=PlanState.STARTED)
        scenario.expect_task(scenario.task_in_hand, state=TaskState.STARTED)
        scenario.expect_stack("idle", "following_plan")
