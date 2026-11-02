from tests.stories.fixtures.main.supervisor_grant_capabilities import configure_grant_capabilities
from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantCliRole


class SupervisorGrantCliAct(SupervisorGrantCliRole):
    """The supervisor can act on task creation and plan priorities."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        configure_grant_capabilities(story, self.supervisor_authority, story.grants.first, {
            "task create": {"on": True, "mode": "act"},
            "plan priorities": {"on": True, "mode": "act"},
        })
