from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
def test_tasks_left_at_the_default_priority_are_asked_about(scenario):
    scenario.user_sets(TasksOptions.PRIORITY_REMIND_TASKS, 2)
    scenario.agent_creates_task("the header")
    scenario.agent_creates_task("the menu")
    scenario.agent_reads()
    scenario.expect_agent_told(TasksNudges.PRIORITIES_REMINDER)
