from tests.stories.fixtures.main.organization_role_task_on_seat import OrganizationRoleTaskOnSeat


class OrganizationRoleTaskClockedIn(OrganizationRoleTaskOnSeat):
    """The owner has read the worker row after the Role worker clocked in."""

    parent = OrganizationRoleTaskOnSeat

    def steps(self, story) -> None:
        worker = story.agents.workers.first()
        result = story.user_opens(f"/journal/workers?ids={worker}")
        result.expect_viewer_passed()

    def expected(self, story) -> None:
        super().expected(story)
