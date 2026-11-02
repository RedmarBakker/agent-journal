from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantCliRole


class SupervisorGrantAreaControl(SupervisorGrantCliRole):
    """The supervisor has an area switch and an explicit task capability setting."""

    parent = SupervisorGrantCliRole
    area_enabled = True
    verb_enabled = False

    def steps(self, story) -> None:
        entry = self.supervisor_authority._latest_entry(story.grants.first)
        grant = self.supervisor_authority._public_grant(entry)
        version_two = self.supervisor_authority._grant_v2(entry, grant)
        capabilities = {
            **version_two["capabilities"],
            "area:plans-and-tasks": {"on": self.area_enabled, "mode": "propose"},
            "task create": {"on": self.verb_enabled, "mode": "act"},
        }
        result = story.user_presses("/_supervisor/v1/enrollment/change", {
            "protocol_version": 1,
            "grant_id": story.grants.first,
            "expected_grant_version": grant["grant_version"],
            "change": {"kind": "configure", "grant": {**version_two, "capabilities": capabilities}},
        })
        result.expect_viewer_passed()
