from journal.features.tasks.tasks_nudges import TasksNudges
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(TaskInHand)
def test_a_wait_with_a_task_in_progress_sends_the_agent_nowhere(scenario):
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("await 'the build' --until false")
    scenario.agent_stops()
    scenario.expect_allowed()


@starts_from(TaskInHand)
def test_a_task_started_during_a_wait_is_carried_on_with_once(scenario):
    scenario.agent_runs("task create 'the header'")
    scenario.agent_runs("await 'the build' --until false")
    scenario.agent_runs("task test 1")
    scenario.agent_stops()
    scenario.expect_refused(TasksNudges.WAIT_NEXT_TASK, n=2)
    scenario.agent_stops()
    scenario.expect_allowed()
