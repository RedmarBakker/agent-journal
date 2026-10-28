from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent


@story(WorkingAgent, end=[Ready])
def test_half_an_hour_of_nothing_with_open_work_asks_the_agent_to_check_in(story):
    story.agent_creates_task("the header")
    story.agent_is_quiet_for(minutes=31)
    story.expect_agent_told(TasksNudges.IDLE_CHECK)


@story(WorkingAgent, end=[Ready])
def test_half_an_hour_of_nothing_with_no_work_says_nothing(story):
    story.agent_is_quiet_for(minutes=31)
    story.expect_agent_not_told(TasksNudges.IDLE_CHECK)
