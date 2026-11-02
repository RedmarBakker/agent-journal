from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantCliRole
from tests.stories.fixtures.state_fixture import StateFixture


class SupervisorGrantCliRoleWithTask(StateFixture):
    """The supervisor's owner fixture exposes its task for the one story that cancels it."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        self.tasks.first = self.supervisor_task_id
        plan = story.user_opens_in(self.supervisor_owner_environment, "/journal/plans")
        plan.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
