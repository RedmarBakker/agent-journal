from journal.models.task_state import TaskState
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.worker_delivered import WorkerDelivered


@scenario(WorkerDelivered)
def test_checked_proofs_let_the_work_be_merged(scenario):
    scenario.agent_runs(f"worker check {scenario.worker} 1")
    scenario.expect_command_passed()
    scenario.agent_runs(f"worker check {scenario.worker} 2")
    scenario.expect_command_passed()
    scenario.agent_runs(f"worker merge {scenario.worker}")
    scenario.expect_command_passed()
    scenario.expect_task(scenario.open_task, state=TaskState.COMPLETED)
