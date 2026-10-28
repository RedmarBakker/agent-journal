from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from tests.scenarios.builder.story_values import starts_from, values_of
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(TaskInHand)
@values_of(TasksOptions.AUTO)
def test_auto_mode_decides_whether_the_next_task_starts(scenario, value):
    scenario.user_sets(TasksOptions.AUTO, value)
    header = scenario.agent_creates_task("the header")
    scenario.agent_runs(f"task complete {scenario.task_in_hand} --how done")
    scenario.expect_task(header, state=TaskState.STARTED if value else TaskState.OPEN)

    scenario.agent_stops()
    scenario.expect_refused_if(value, TasksNudges.TASK_CONTINUATION, name=f"task {header}")


@starts_from(TaskInHand)
def test_a_paused_task_is_offered_as_a_choice(scenario):
    scenario.user_sets(TasksOptions.AUTO, True)
    scenario.agent_creates_task("the header")
    scenario.agent_runs(f"task pause {scenario.task_in_hand} 'the header first'")

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.PAUSED_CHOICE)


@starts_from(TaskInHand)
def test_an_agent_stopped_with_work_in_hand_is_woken(scenario):
    scenario.user_sets(TasksOptions.WAKE_MINUTES, 10)
    scenario.agent_stops()
    scenario.agent_is_quiet_for(minutes=11)
    scenario.expect_agent_told(TasksNudges.STOPPED_WITH_WORK)
