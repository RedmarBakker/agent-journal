from journal.features.tasks.tasks_nudges import TasksNudges
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
def test_stuck_with_tasks_open_is_refused(scenario):
    scenario.agent_creates_task("the header")
    scenario.agent_runs_in_the_shell("journal stuck 'the build fails'")
    scenario.expect_refused(TasksNudges.IMPASSE_REFUSAL)
