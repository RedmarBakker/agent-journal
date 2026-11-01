from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture


class FreshAgentBeforeFirstHook(StateFixture):
    """A new main agent's Ready state exists before its first session hook."""

    stack = (Ready,)

    def steps(self, story) -> None:
        pass

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
