from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantCliRole
from tests.stories.fixtures.main.supervisor_grant_capabilities import configure_grant_capabilities


class SupervisorGrantAreaControl(SupervisorGrantCliRole):
    """The supervisor has an area switch and an explicit task capability setting."""

    parent = SupervisorGrantCliRole
    area_enabled = True
    verb_enabled = False

    def steps(self, story) -> None:
        configure_grant_capabilities(story, self.supervisor_authority, story.grants.first, {
            "area:plans-and-tasks": {"on": self.area_enabled, "mode": "propose"},
            "task create": {"on": self.verb_enabled, "mode": "act"},
        })
