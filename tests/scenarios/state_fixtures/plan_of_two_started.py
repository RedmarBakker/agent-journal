from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork
from tests.scenarios.builder.stack_states import FOLLOWING_PLAN, IDLE
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class PlanOfTwoStarted(StateFixture):
    """The user made a plan with two tasks and approved it in the viewer, and the agent at work started it: scenario.plan, its first task in hand as scenario.task_in_hand and the next as scenario.next_plan_task."""

    stack = (IDLE, FOLLOWING_PLAN)

    builds_on = AgentAtWork

    def steps(self, scenario) -> None:
        scenario.provide(PlanOfTwoStarted, "plan", scenario.user_creates_plan("p", "b"))
        scenario.provide(PlanOfTwoStarted, "task_in_hand", scenario.user_adds_plan_task(scenario.plan, "first"))
        scenario.provide(PlanOfTwoStarted, "next_plan_task", scenario.user_adds_plan_task(scenario.plan, "second"))
        scenario.user_approves_plan(scenario.plan)
        scenario.agent_runs(f"plan start {scenario.plan}")

    def expected(self, scenario) -> None:
        scenario.expect_plan(scenario.plan, state=PlanState.STARTED)
        scenario.expect_task(scenario.task_in_hand, state=TaskState.STARTED)
