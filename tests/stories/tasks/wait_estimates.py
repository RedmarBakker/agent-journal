from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent


@story(WorkingAgent, end=[Ready, ExternalWait])
def test_the_next_open_task_is_named_a_minute_into_a_wait(story):
    header = story.agent_creates_task("the header")
    story.agent_runs("await 'the build' --until false")
    story.agent_is_quiet_for(minutes=1.1)
    story.expect_agent_told(TasksNudges.WAIT_NEXT_TASK, n=header)


@story(WorkingAgent, end=[Ready, ExternalWait])
def test_a_long_idle_wait_asks_the_agent_to_check_it(story):
    story.agent_runs("await 'the build' --until false")
    story.agent_is_quiet_for(minutes=5.1)
    story.expect_agent_told(TasksNudges.WAIT_CHECK)
