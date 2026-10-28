from tests.scenarios.builder.stack_states import AWAITING, IDLE
from tests.scenarios.builder.story_values import scenario, values
from tests.scenarios.state_fixtures.task_with_points_open import TaskWithPointsOpen


@scenario(TaskWithPointsOpen, end=[IDLE, AWAITING])
@values(["task create 'more work'", "plan create p --brief b", "message send hello", "settings set tasks.auto off", "question ask 'go on?' --options yes no"])
def test_a_worker_runs_only_the_verbs_its_helper_file_names(scenario, value):
    worker = scenario.agent_dispatches_worker("Lady Lovelace", scenario.open_task)
    scenario.worker_clocks_in(worker)
    scenario.worker_tries(worker, value)
    scenario.expect_command_refused()

