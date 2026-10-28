from journal.engine.states.ended import Ended
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.working_agent import WorkingAgent


class EndedSession(StateFixture):
    """The agent at work ended its session, so no session of it runs."""

    stack = (Ready, Ended)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.agent_ends_the_session()

    def expected(self, story) -> None:
        story.expect_stack(Ready, Ended)
