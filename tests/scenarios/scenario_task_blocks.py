from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand)
def test_a_task_blocked_on_another_is_taken_up_when_that_one_closes(scenario):
    header = scenario.agent_creates_task("the header")
    scenario.agent_runs(f"task block {header} --on task:{scenario.task_in_hand}")
    scenario.expect_task(header, state=TaskState.BLOCKED)
    scenario.agent_runs(f"task complete {scenario.task_in_hand} --how done")
    scenario.expect_task(header, state=TaskState.STARTED)
    scenario.expect_agent_told(TasksNudges.TASK_REOPENED, n=header)
