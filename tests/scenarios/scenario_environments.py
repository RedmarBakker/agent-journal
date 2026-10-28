from journal.features.plans.plans_nudges import PlansNudges
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.scenarios.builder.stack_states import IDLE, WORKING
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.plan_of_two_started import PlanOfTwoStarted
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand
from tests.scenarios.state_fixtures.worker_delivered import WorkerDelivered


@scenario(TaskInHand, end=[IDLE, WORKING])
def test_a_task_in_hand_stays_unless_the_transfer_is_forced(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other}")
    scenario.expect_command_refused()
    scenario.expect_task(scenario.task_in_hand, state=TaskState.STARTED)
    assert scenario.task_in_hand not in scenario.task_numbers_in(other)


@scenario(TaskInHand, end=[IDLE])
def test_a_forced_transfer_of_the_task_in_hand_pauses_it_and_frees_the_agent(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other} --force")
    scenario.expect_command_passed()
    assert scenario.task_in_hand in scenario.task_numbers_in(other) and scenario.task_in_hand not in scenario.task_numbers_in("main")
    scenario.agent_stops()
    scenario.expect_allowed()


@scenario(TaskInHand, end=[IDLE, WORKING])
def test_a_transferred_paused_task_is_no_longer_offered_here(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task pause {scenario.task_in_hand} 'the other environment takes it'")
    footer = scenario.agent_creates_task("Write the footer")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other}")
    scenario.expect_command_passed()
    scenario.agent_stops()
    scenario.expect_agent_not_told(TasksNudges.PAUSED_CHOICE)
    scenario.expect_task(footer, state=TaskState.STARTED)


@scenario(PlanOfTwoStarted, end=[IDLE])
def test_a_plan_task_moves_only_by_force_and_the_plan_finishes_without_it(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task transfer {scenario.next_plan_task} {other}")
    scenario.expect_command_refused()
    scenario.agent_runs(f"task transfer {scenario.next_plan_task} {other} --force")
    scenario.expect_command_passed()
    scenario.agent_runs(f"task complete {scenario.task_in_hand} --how done")
    scenario.expect_plan(scenario.plan, state=PlanState.FINISHED)
    scenario.expect_agent_told(PlansNudges.PLAN_FINISHED, n=scenario.plan)
    assert scenario.next_plan_task in scenario.task_numbers_in(other)


@scenario(WorkerDelivered, end=[IDLE])
def test_a_task_a_worker_holds_is_never_transferred(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task transfer {scenario.open_task} {other} --force")
    scenario.expect_command_refused()
    scenario.expect_worker(scenario.worker, state=WorkerState.DELIVERED)
    assert scenario.open_task not in scenario.task_numbers_in(other)
