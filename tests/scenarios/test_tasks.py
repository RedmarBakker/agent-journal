from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.state_fixtures.plan_just_started import PlanJustStarted
from tests.state_fixtures.task_in_hand import TaskInHand


def test_a_task_outside_a_plan_is_worked_on_top_of_the_plan_and_the_plan_stays_paused(scenario):
    scenario.starts_from(PlanJustStarted)
    scenario.agent_runs("task pause 1 'something else first'")
    scenario.agent_runs("task create outside --start")
    scenario.expect_stack("idle", "following_plan", "working")

    scenario.user_runs("plan pause 1")
    scenario.expect_plan(1, state=PlanState.PAUSED)

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION)

    scenario.agent_runs("task complete 2 --how done")
    scenario.expect_task(2, state=TaskState.COMPLETED)
    scenario.expect_plan(1, state=PlanState.PAUSED)


def test_a_task_put_in_testing_leaves_the_agents_hand_and_a_stop_is_let_through(scenario):
    scenario.starts_from(TaskInHand)
    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION)

    scenario.agent_runs("task test 1")
    scenario.expect_task(1, state=TaskState.TESTING)
    scenario.expect_stack("idle")

    scenario.agent_stops()
    scenario.expect_allowed()


def test_a_test_run_on_a_task_long_in_progress_asks_once_whether_it_tests_that_task(scenario):
    scenario.starts_from(TaskInHand)
    scenario.user_sets(TasksOptions.TESTING_SUGGESTION_MINUTES, 0)
    scenario.user_sets(TasksOptions.TESTING_SUGGESTION_TOOL_USES, 3)

    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_not_told(TasksNudges.TESTING_SUGGESTION)

    scenario.agent_reads("a.py")
    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_told(TasksNudges.TESTING_SUGGESTION, n=1)

    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_not_told(TasksNudges.TESTING_SUGGESTION)
