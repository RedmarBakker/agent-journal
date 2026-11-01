from journal.features.tasks.states.external_wait import CHECK_REMINDER, NEXT_TASK_DELAY, ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_next_open_task_is_named_a_minute_into_a_wait(story):
    header = story.agent_creates_task(story.agents.subject, "the header")
    story.agent_runs(story.agents.subject, "await 'the build' --until false")
    result = story.agent_is_quiet_past(story.agents.subject, NEXT_TASK_DELAY.amount)
    result.expect_agent_told(story.agents.subject, TasksNudges.WAIT_NEXT_TASK, n=header)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_long_idle_wait_asks_the_agent_to_check_it(story):
    story.agent_runs(story.agents.subject, "await 'the build' --until false")
    result = story.agent_is_quiet_past(story.agents.subject, CHECK_REMINDER.amount)
    result.expect_agent_told(story.agents.subject, TasksNudges.WAIT_CHECK)
    story.expect_stack(story.agents.subject, Ready, ExternalWait)
