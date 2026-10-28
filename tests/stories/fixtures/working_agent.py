from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture


class WorkingAgent(StateFixture):
    """The main agent has started its session and read the overview, so its writes go through."""

    stack = (Ready,)

    def steps(self, story) -> None:
        story.agent_starts_a_session()
        story.agent_looks_at_the_overview()

    def expected(self, story) -> None:
        story.expect_stack(Ready)
