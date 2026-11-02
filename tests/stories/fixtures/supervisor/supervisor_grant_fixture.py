from journal.supervisor_authority import SupervisorAuthority
from tests.stories.fixtures.state_fixture import StateFixture


class SupervisorGrantFixture(StateFixture):
    """A supervisor's current plan driver is running in the story."""

    def restore_on(self, story) -> None:
        super().restore_on(story)
        authority = story.app.container.get(SupervisorAuthority)
        story.monkeypatch.setattr(type(authority.agents), "is_running", lambda _self, _environment: True)
