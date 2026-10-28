from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.plan_just_started import PlanJustStarted
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(PlanJustStarted)
def test_a_task_outside_a_plan_is_worked_on_top_of_it(scenario):
    scenario.agent_runs("task pause 1 'something else first'")
    scenario.agent_runs("task create outside --start")
    scenario.expect_stack("idle", "following_plan", "working")

    scenario.user_pauses_plan(1)
    scenario.expect_plan(1, state=PlanState.PAUSED)

    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION)

    scenario.agent_runs("task complete 2 --how done")
    scenario.expect_task(2, state=TaskState.COMPLETED)
    scenario.expect_plan(1, state=PlanState.PAUSED)


@starts_from(TaskInHand)
def test_a_task_in_testing_leaves_the_agents_hand(scenario):
    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION)

    scenario.agent_runs("task test 1")
    scenario.expect_task(1, state=TaskState.TESTING)
    scenario.expect_stack("idle")

    scenario.agent_stops()
    scenario.expect_allowed()


@starts_from(TaskInHand)
def test_a_test_run_on_a_long_task_suggests_testing(scenario):
    scenario.user_sets(TasksOptions.TESTING_SUGGESTION_MINUTES, 0)
    scenario.user_sets(TasksOptions.TESTING_SUGGESTION_TOOL_USES, 3)

    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_not_told(TasksNudges.TESTING_SUGGESTION)

    scenario.agent_reads("a.py")
    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_told(TasksNudges.TESTING_SUGGESTION, n=1)

    scenario.agent_runs_in_the_shell("pytest -q")
    scenario.expect_agent_not_told(TasksNudges.TESTING_SUGGESTION)
