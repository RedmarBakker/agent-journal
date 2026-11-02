from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.supervisor_grant_owner import SupervisorGrantOwner


class SupervisorGrantPaused(SupervisorGrantOwner):
    """The owner has paused the supervisor grant."""

    parent = SupervisorGrantOwner

    def steps(self, story) -> None:
        result = story.user_presses("/_supervisor/v1/enrollment/change", {
            "protocol_version": 1,
            "grant_id": story.grants.first,
            "expected_grant_version": 1,
            "change": {"kind": "off"},
        })
        result.expect_viewer_passed()
        result.expect_viewer_part(("grant_version",), 2)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
