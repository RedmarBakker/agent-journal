from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class RecordedDomainDeliveryEstimates(StateFixture):
    """Delivery plans record task estimates."""

    parent = WorkingAgent
    stack = (Ready,)

    def steps(self, story) -> None:
        story.user_sets(EstimatesOptions.MODE, "record")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
