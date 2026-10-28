from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.worker_state import WorkerState
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.task_with_points_open import TaskWithPointsOpen


@starts_from(TaskWithPointsOpen)
def test_a_worker_proves_each_point_and_its_work_waits_for_the_check(scenario):
    worker = scenario.agent_dispatches_worker("Lady Lovelace", scenario.open_task)
    scenario.worker_clocks_in(worker)
    scenario.worker_proves(worker, 1, "parser.py:12, test_reads passes")
    scenario.worker_proves(worker, 2, "parser.py:30, test_names passes")
    scenario.worker_clocks_out(worker, "the parser is done")
    scenario.expect_worker(worker, state=WorkerState.DELIVERED)
    scenario.expect_agent_told(WorkersNudges.WORK_READY)
