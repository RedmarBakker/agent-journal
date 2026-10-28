from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.tasks.tasks_options import TasksOptions
from tests.scenarios.builder.story_values import scenario, settings
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
@settings(TasksOptions.PRIORITY_REMIND_TASKS, 2)
def test_tasks_left_at_the_default_priority_are_asked_about(scenario):
    scenario.repeat(int(scenario.setting(TasksOptions.PRIORITY_REMIND_TASKS)), lambda: scenario.agent_creates_task("more work"))
    scenario.agent_reads()
    scenario.expect_agent_told(TasksNudges.PRIORITIES_REMINDER)
