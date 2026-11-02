from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.supervisor_grant_owner import SupervisorGrantOwner
from tests.test_supervisor_authority import enrollment


class SupervisorGrantReplacementOwner(SupervisorGrantOwner):
    """The user owns a grant and a replacement enrollment for its plan."""

    parent = SupervisorGrantOwner

    def steps(self, story) -> None:
        self.grants.replacement = enrollment(self.supervisor_seed, "bounded_write")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
