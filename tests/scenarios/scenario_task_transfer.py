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


@scenario(TaskInHand, end=[IDLE])
def test_a_task_in_progress_moves_only_by_force_and_arrives_in_progress(scenario):
    other = scenario.another_environment("other")
    scenario.session_starts_in(other, "s9")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other}")
    scenario.expect_command_refused()
    scenario.expect_task(scenario.task_in_hand, state=TaskState.STARTED)
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other} --force")
    scenario.expect_command_passed()
    assert scenario.task_states_in(other).get(scenario.task_in_hand) == TaskState.STARTED
    assert scenario.task_in_hand not in scenario.task_numbers_in("main")
    scenario.expect_told_in(other, TasksNudges.TASK_ARRIVED, n=scenario.task_in_hand)
    scenario.agent_stops()
    scenario.expect_allowed()


@scenario(TaskInHand, end=[IDLE])
def test_a_task_in_progress_arrives_paused_where_a_task_is_already_in_progress(scenario):
    other = scenario.another_environment("other")
    theirs = scenario.agent_in_starts_task(other, "s9", "Their own work")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other} --force")
    scenario.expect_command_passed()
    states = scenario.task_states_in(other)
    assert states.get(scenario.task_in_hand) == TaskState.PAUSED and states.get(theirs) == TaskState.STARTED, states


@scenario(TaskInHand, end=[IDLE])
def test_a_task_in_testing_moves_only_by_force_and_stays_in_testing(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task test {scenario.task_in_hand}")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other}")
    scenario.expect_command_refused()
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other} --force")
    scenario.expect_command_passed()
    assert scenario.task_states_in(other).get(scenario.task_in_hand) == TaskState.TESTING


@scenario(TaskInHand, end=[IDLE, WORKING])
def test_a_paused_task_arrives_paused_and_is_no_longer_offered_here(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task pause {scenario.task_in_hand} 'the other environment takes it'")
    footer = scenario.agent_creates_task("Write the footer")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other}")
    scenario.expect_command_passed()
    assert scenario.task_states_in(other).get(scenario.task_in_hand) == TaskState.PAUSED
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
    assert scenario.task_states_in(other).get(scenario.next_plan_task) == TaskState.OPEN


@scenario(WorkerDelivered, end=[IDLE])
def test_a_task_a_worker_holds_is_never_transferred(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task transfer {scenario.open_task} {other} --force")
    scenario.expect_command_refused()
    scenario.expect_worker(scenario.worker, state=WorkerState.DELIVERED)
    assert scenario.open_task not in scenario.task_numbers_in(other)
