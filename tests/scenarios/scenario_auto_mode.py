from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from tests.scenarios.builder.stack_states import IDLE, WORKING
from tests.scenarios.builder.story_values import scenario, values_of
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand)
@values_of(TasksOptions.AUTO)
def test_auto_mode_decides_whether_the_next_task_starts(scenario, value):
    scenario.user_sets(TasksOptions.AUTO, value)
    header = scenario.agent_creates_task("the header")
    scenario.agent_runs(f"task complete {scenario.task_in_hand} --how done")
    scenario.expect_task(header, state=TaskState.STARTED if value else TaskState.OPEN)

    scenario.agent_stops()
    scenario.expect_refused_if(value, TasksNudges.TASK_CONTINUATION, name=f"task {header}")
    scenario.expect_end(*([IDLE, WORKING] if value else [IDLE]))
