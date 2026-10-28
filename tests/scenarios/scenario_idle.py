from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


def test_in_auto_mode_finishing_the_task_in_hand_starts_the_next_open_one_and_the_stop_carries_on_with_it(scenario):
    scenario.starts_from(TaskInHand)
    scenario.user_sets(TasksOptions.AUTO, True)
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("task complete 1 --how done")
    scenario.expect_task(2, state=TaskState.STARTED)

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION, name="task 2")


def test_out_of_auto_mode_finishing_the_task_in_hand_lets_the_stop_through_and_starts_nothing(scenario):
    scenario.starts_from(TaskInHand)
    scenario.user_sets(TasksOptions.AUTO, False)
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("task complete 1 --how done")

    scenario.agent_stops()
    scenario.expect_allowed()
    scenario.expect_task(2, state=TaskState.OPEN)


def test_a_paused_task_of_the_agents_own_beside_an_open_one_is_offered_as_a_choice_at_the_stop(scenario):
    scenario.starts_from(TaskInHand)
    scenario.user_sets(TasksOptions.AUTO, True)
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("task pause 1 'the header first'")

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.PAUSED_CHOICE)
