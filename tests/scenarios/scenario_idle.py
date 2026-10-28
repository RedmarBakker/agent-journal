from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.task_state import TaskState
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(TaskInHand)
def test_auto_mode_starts_the_next_task(scenario):
    scenario.user_sets(TasksOptions.AUTO, True)
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("task complete 1 --how done")
    scenario.expect_task(2, state=TaskState.STARTED)

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION, name="task 2")


@starts_from(TaskInHand)
def test_without_auto_mode_nothing_starts(scenario):
    scenario.user_sets(TasksOptions.AUTO, False)
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("task complete 1 --how done")

    scenario.agent_stops()
    scenario.expect_allowed()
    scenario.expect_task(2, state=TaskState.OPEN)


@starts_from(TaskInHand)
def test_a_paused_task_is_offered_as_a_choice(scenario):
    scenario.user_sets(TasksOptions.AUTO, True)
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("task pause 1 'the header first'")

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.PAUSED_CHOICE)
