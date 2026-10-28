from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.working_agent import WorkingAgent


@story(WorkingAgent, end=[Ready])
def test_stuck_with_tasks_open_is_refused(story):
    story.agent_creates_task("the header")
    story.agent_runs_in_the_shell("journal stuck 'the build fails'")
    story.expect_refused(TasksNudges.IMPASSE_REFUSAL)
