from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.scenarios.builder.stack_states import AWAITING, IDLE
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.plan_approved import PlanApproved
from tests.scenarios.state_fixtures.plan_just_started import PlanJustStarted
from tests.scenarios.state_fixtures.plan_of_two_started import PlanOfTwoStarted


@scenario(PlanOfTwoStarted, end=[IDLE])
def test_a_plans_tasks_follow_in_order_until_it_finishes(scenario):
    scenario.agent_runs(f"task complete {scenario.task_in_hand} --how done")
    scenario.expect_task(scenario.next_plan_task, state=TaskState.STARTED)
    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.TASK_CONTINUATION, name=f"task {scenario.next_plan_task}")

    scenario.agent_runs(f"task complete {scenario.next_plan_task} --how done")
    scenario.expect_plan(scenario.plan, state=PlanState.FINISHED)
    scenario.expect_agent_told(PlansNudges.PLAN_FINISHED, n=scenario.plan)


@scenario(PlanJustStarted, end=[IDLE])
def test_a_plan_the_user_pauses_stays_quiet_at_the_stop(scenario):
    scenario.user_pauses_plan(scenario.plan)
    scenario.agent_runs(f"task pause {scenario.task_in_hand} 'later'")
    scenario.agent_stops()
    scenario.expect_allowed()


@scenario(PlanApproved, end=[IDLE, AWAITING])
def test_a_plan_given_whole_to_a_worker_is_delegated(scenario):
    scenario.agent_dispatches_worker_on_plan("Lady Lovelace", scenario.plan)
    scenario.expect_plan(scenario.plan, state=PlanState.DELEGATED)
