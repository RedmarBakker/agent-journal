from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture


class NewSession(StateFixture):
    """The main agent's session has just started and it has not looked at the overview yet."""

    stack = (Ready,)

    def steps(self, story) -> None:
        story.agent_starts_a_session()

    def expected(self, story) -> None:
        story.expect_stack(Ready)
