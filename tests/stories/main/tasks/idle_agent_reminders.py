from journal.features.tasks.states.ready import IDLE_CHECK_DELAY_SECONDS, Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from journal.features.workers.workers_options import BUILDER_MODE
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE)
def test_half_an_hour_of_nothing_with_open_work_asks_the_agent_to_check_in(story):
    story.agent_creates_task("the header")
    story.agent_is_quiet_past(IDLE_CHECK_DELAY_SECONDS)
    story.expect_agent_told(TasksNudges.IDLE_CHECK)
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE)
def test_half_an_hour_of_nothing_with_no_work_says_nothing(story):
    story.agent_is_quiet_past(IDLE_CHECK_DELAY_SECONDS)
    story.expect_agent_not_told(TasksNudges.IDLE_CHECK)
    story.expect_stack(Ready)
