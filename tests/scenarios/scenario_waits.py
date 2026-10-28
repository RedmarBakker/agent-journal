from journal.features.tasks.tasks_nudges import TasksNudges
from journal.models.task_state import TaskState
from tests.scenarios.builder.stack_states import AWAITING, IDLE, WORKING
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand, end=[IDLE, WORKING, AWAITING])
def test_a_wait_with_a_task_in_progress_sends_the_agent_nowhere(scenario):
    scenario.agent_creates_task("the header")
    scenario.agent_runs("await 'the build' --until false")
    scenario.agent_stops()
    scenario.expect_allowed()
    scenario.expect_task(scenario.task_in_hand, state=TaskState.STARTED)


@scenario(TaskInHand, end=[IDLE, WORKING, AWAITING])
def test_a_task_started_during_a_wait_is_carried_on_with_once(scenario):
    header = scenario.agent_creates_task("the header")
    scenario.agent_runs("await 'the build' --until false")
    scenario.agent_runs(f"task test {scenario.task_in_hand}")
    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.WAIT_NEXT_TASK, n=header)
    scenario.agent_stops()
    scenario.expect_allowed()
