from journal.features.tasks.states.impasse import Impasse
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class AgentImpasse(StateFixture):
    """The agent at work with nothing open said it is stuck, and the journal sends it nothing until it moves again."""

    stack = (Ready, Impasse)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.agent_runs("stuck 'the build fails and nothing else is open'")

    def expected(self, story) -> None:
        story.expect_stack(Ready, Impasse)
