from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.plan_of_two_started import PlanOfTwoStarted


@starts_from(PlanOfTwoStarted)
def test_a_plans_tasks_follow_in_order_until_it_finishes(scenario):
    scenario.agent_runs("task complete 1 --how done")
    scenario.expect_task(2, state=TaskState.STARTED)
    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION, name="task 2")

    scenario.agent_runs("task complete 2 --how done")
    scenario.expect_plan(1, state=PlanState.FINISHED)
    scenario.expect_agent_told(PlansNudges.PLAN_FINISHED, n=1)


@starts_from(PlanOfTwoStarted)
def test_a_plan_the_user_pauses_stays_quiet_at_the_stop(scenario):
    scenario.user_pauses_plan(1)
    scenario.agent_runs("task pause 1 'later'")
    scenario.agent_stops()
    scenario.expect_allowed()
