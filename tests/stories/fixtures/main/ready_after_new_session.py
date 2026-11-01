from journal.features.tasks.states.ready import IDLE_CHECK_DELAY_SECONDS, Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from tests.stories.fixtures.main.working_agent import WorkingAgent


class ReadyAfterNewSession(WorkingAgent):
    """A main agent has started a new session after an old idle state."""

    parent = WorkingAgent

    def steps(self, story) -> None:
        quiet = story.agent_is_quiet_past(story.agents.main, IDLE_CHECK_DELAY_SECONDS)
        quiet.expect_agent_not_told(story.agents.main, TasksNudges.IDLE_CHECK)
        story.agent_ends_the_session(story.agents.main)
        started = story.agent_starts_a_session(story.agents.main)
        started.expect_agent_not_told(story.agents.main, TasksNudges.IDLE_CHECK)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
