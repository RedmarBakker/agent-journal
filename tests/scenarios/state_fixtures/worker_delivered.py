from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.scenarios.state_fixtures.state_fixture import StateFixture
from tests.scenarios.state_fixtures.task_with_points_open import TaskWithPointsOpen


class WorkerDelivered(StateFixture):
    """A worker sent on the open task clocked in, proved both points and clocked out, its work waiting for the agent's check: scenario.worker."""

    builds_on = TaskWithPointsOpen

    def steps(self, scenario) -> None:
        scenario.worker = scenario.agent_dispatches_worker("Lady Lovelace", scenario.open_task)
        scenario.worker_clocks_in(scenario.worker)
        scenario.worker_proves(scenario.worker, 1, "parser.py:12, test_reads passes")
        scenario.worker_proves(scenario.worker, 2, "parser.py:30, test_names passes")
        scenario.worker_clocks_out(scenario.worker, "the parser is done")

    def expected(self, scenario) -> None:
        scenario.expect_worker(scenario.worker, state=WorkerState.DELIVERED)
        scenario.expect_agent_told(WorkersNudges.WORK_READY)
