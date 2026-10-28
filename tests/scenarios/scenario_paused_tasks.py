from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from tests.scenarios.builder.stack_states import CHOOSING_PAUSED_WORK, IDLE
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand, end=[IDLE, CHOOSING_PAUSED_WORK])
def test_a_paused_task_is_offered_as_a_choice(scenario):
    scenario.user_sets(TasksOptions.AUTO, True)
    scenario.agent_creates_task("the header")
    scenario.agent_runs(f"task pause {scenario.task_in_hand} 'the header first'")

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.PAUSED_CHOICE)
