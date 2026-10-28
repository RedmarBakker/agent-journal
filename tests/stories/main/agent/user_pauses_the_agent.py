from journal.features.pausing.pausing_nudges import PausingNudges
from journal.features.pausing.states.user_pause import UserPause
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.started_task import StartedTask


@story(StartedTask, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_paused_agent_is_refused_its_writes_and_told_to_carry_on_when_resumed(story):
    story.user_pauses_the_agent()
    story.expect_stack(Ready, Working, UserPause)
    story.agent_writes("footer.py")
    story.expect_refused(PausingNudges.PAUSED)
    story.user_resumes_the_agent()
    story.expect_agent_told(PausingNudges.RESUMED)
    story.expect_task(story.start.started_task, state=TaskState.STARTED)
    story.expect_stack(Ready, Working)
