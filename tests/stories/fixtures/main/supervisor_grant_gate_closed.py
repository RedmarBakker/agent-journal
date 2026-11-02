from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.supervisor_grant_paused import SupervisorGrantPaused


class SupervisorGrantGateClosed(SupervisorGrantPaused):
    """The owner's supervisor installation is awaiting its restore review."""

    parent = SupervisorGrantPaused

    def steps(self, story) -> None:
        self.supervisor_authority.restore_installation(self.supervisor_owner, story.grants.first)
        story.observed("the installation restore review is active", None, None)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
