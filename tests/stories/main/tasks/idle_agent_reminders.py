from journal.features.tasks.states.ready import IDLE_CHECK_DELAY_SECONDS, Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_half_an_hour_of_nothing_with_open_work_asks_the_agent_to_check_in(story):
    story.agent_creates_task(story.agents.subject, "the header")
    result = story.agent_is_quiet_past(story.agents.subject, IDLE_CHECK_DELAY_SECONDS)
    result.expect_agent_told(story.agents.subject, TasksNudges.IDLE_CHECK)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_half_an_hour_of_nothing_with_no_work_says_nothing(story):
    result = story.agent_is_quiet_past(story.agents.subject, IDLE_CHECK_DELAY_SECONDS)
    result.expect_agent_not_told(story.agents.subject, TasksNudges.IDLE_CHECK)
    story.expect_stack(story.agents.subject, Ready)
