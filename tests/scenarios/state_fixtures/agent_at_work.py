from tests.scenarios.builder.stack_states import IDLE
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class AgentAtWork(StateFixture):
    """The main agent has started its session and read the overview, so its writes go through."""

    stack = (IDLE,)

    def steps(self, scenario) -> None:
        scenario.agent_starts_a_session()
        scenario.agent_looks_at_the_overview()

    def expected(self, scenario) -> None:
        scenario.expect_stack("idle")
