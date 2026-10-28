from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.started_task import StartedTask
from tests.stories.fixtures.state_fixture import StateFixture


class TaskTakeover(StateFixture):
    """A second session of the agent at work started and took over the agent and its task in hand; the story's main agent is that new session."""

    stack = (Ready, Working)

    parent = StartedTask

    def steps(self, story) -> None:
        story.second_session_starts()

    def expected(self, story) -> None:
        story.expect_agent_told(BriefingNudges.TAKEOVER)
        story.expect_agent_session(story.main_session())
        story.expect_task(self.started_task, state=TaskState.STARTED)
        story.expect_stack(Ready, Working)
