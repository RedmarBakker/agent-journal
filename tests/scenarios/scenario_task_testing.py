from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from tests.scenarios.builder.stack_states import IDLE
from tests.scenarios.builder.story_values import scenario, settings, values
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand)
@settings(TasksOptions.TESTING_SUGGESTION_MINUTES, 0)
@settings(TasksOptions.TESTING_SUGGESTION_TOOL_USES, 3)
def test_a_test_run_on_a_long_task_suggests_testing(scenario):
    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_not_told(TasksNudges.TESTING_SUGGESTION)

    scenario.agent_reads("a.py")
    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_told(TasksNudges.TESTING_SUGGESTION, n=scenario.task_in_hand)

    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_not_told(TasksNudges.TESTING_SUGGESTION)


@scenario(TaskInHand, end=[IDLE])
@values([0, 3])
def test_a_task_in_testing_follows_its_run(scenario, value):
    scenario.agent_runs(f"task test {scenario.task_in_hand}")
    run = scenario.agent_runs_a_command(f"sh -c 'seq 1 300; exit {value}'")
    scenario.agent_runs(f"output test {run}")
    scenario.expect_task(scenario.task_in_hand, state=TaskState.PAUSED if value else TaskState.COMPLETED)
