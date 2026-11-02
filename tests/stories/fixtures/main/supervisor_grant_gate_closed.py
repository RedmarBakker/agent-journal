from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.supervisor_grant_owner import SupervisorGrantOwner
from tests.stories.fixtures.state_fixture import StateFixture


class SupervisorGrantGateClosed(StateFixture):
    """The owner's supervisor installation is awaiting its restore review."""

    parent = SupervisorGrantOwner

    def steps(self, story) -> None:
        self.supervisor_authority.restore_installation(self.supervisor_owner, story.grants.first)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
