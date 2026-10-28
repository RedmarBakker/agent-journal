from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from tests.scenarios.builder.story_values import scenario, settings
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand)
@settings(TasksOptions.WAKE_MINUTES, 10)
def test_an_agent_stopped_with_work_in_hand_is_woken(scenario):
    scenario.agent_stops()
    scenario.agent_is_quiet_for(minutes=scenario.setting(TasksOptions.WAKE_MINUTES) + 1)
    scenario.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
    scenario.expect_task(scenario.task_in_hand, state=TaskState.STARTED)
