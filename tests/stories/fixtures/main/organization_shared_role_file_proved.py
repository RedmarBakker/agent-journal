from tests.stories.fixtures.main.organization_shared_role_task_clocked_in import OrganizationSharedRoleTaskClockedIn


class OrganizationSharedRoleFileProved(OrganizationSharedRoleTaskClockedIn):
    """A shared Role seat has written and proved its file."""

    parent = OrganizationSharedRoleTaskClockedIn

    def steps(self, story) -> None:
        worker = story.agents.workers.first()
        story.agent_writes_from_organization_role_seat(worker, "role:alpha/shared", "SECURITY.md").expect_allowed(worker)
        story.the_project_holds_a_file("SECURITY.md", b"The shared Role result is ready.\n")
        story.agent_proves(worker, 1, "SECURITY.md:1; the shared result is present").expect_command_passed()
