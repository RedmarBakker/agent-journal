from tests.scenarios.builder.stack_states import IDLE, WORKING
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork, end=[IDLE, WORKING])
def test_stack_changes_are_counted_and_the_ones_no_story_walks_marked(scenario):
    scenario.agent_takes_a_task("count the stack changes")
    scenario.scenario_run_walked(f"no state > {IDLE} on session_started")
    scenario.agent_runs("developer transitions --hours 1")
    scenario.expect_command_passed()
    walked = scenario.expect_command_line(f"no state > {IDLE} on session_started")
    assert "no story walks it" not in walked
    scenario.expect_command_line("1", f"{IDLE} > {WORKING} on task_started", "no story walks it")
