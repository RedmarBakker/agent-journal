from tests.scenarios.builder.stack_states import IDLE
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@scenario(TaskInHand, end=[IDLE])
def test_a_task_transferred_to_another_environment_leaves_this_one(scenario):
    other = scenario.another_environment("other")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other}")
    scenario.expect_command_refused()
    scenario.agent_runs(f"task pause {scenario.task_in_hand} 'the other environment takes it'")
    scenario.agent_runs(f"task transfer {scenario.task_in_hand} {other}")
    scenario.expect_command_passed()
    assert scenario.task_in_hand in scenario.task_numbers_in(other)
    assert scenario.task_in_hand not in scenario.task_numbers_in("main")
