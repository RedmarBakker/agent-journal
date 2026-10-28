from journal.models.plan_state import PlanState
from tests.scenarios.builder.stack_states import AWAITING, IDLE
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.plan_approved import PlanApproved


@scenario(PlanApproved, end=[IDLE, AWAITING])
def test_a_plan_given_whole_to_a_worker_is_delegated(scenario):
    scenario.agent_dispatches_worker_on_plan("Lady Lovelace", scenario.plan)
    scenario.expect_plan(scenario.plan, state=PlanState.DELEGATED)
