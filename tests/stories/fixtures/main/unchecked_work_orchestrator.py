from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.support.mode_measures import ORCHESTRATOR_SPECS
from tests.stories.fixtures.main.orchestrator_worker_delivered import OrchestratorWorkerDelivered
from tests.stories.fixtures.state_fixture import StateFixture

CLEARING_WAIT = "clearing_wait"

CLEARING_WAIT_RANGE = next(spec.range for spec in ORCHESTRATOR_SPECS if spec.key == CLEARING_WAIT)


class UncheckedWorkOrchestrator(StateFixture):
    """The orchestrator left its worker's delivered work unchecked for longer than its fitness range allows, measured on the clock."""

    stack = (Orchestrating,)

    parent = OrchestratorWorkerDelivered

    def steps(self, story) -> None:
        story.agent_is_quiet_for(minutes=CLEARING_WAIT_RANGE.fail_level * 2)

    def expected(self, story) -> None:
        story.expect_stack(Orchestrating)
