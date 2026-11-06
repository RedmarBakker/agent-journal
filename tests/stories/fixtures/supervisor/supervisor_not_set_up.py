from tests.stories.fixtures.main.new_session import NewSession
from tests.test_supervisor_authority import seeded


class SupervisorNotSetUp(NewSession):
    """An owner plan exists, but no supervisor grant has been enrolled."""

    parent = NewSession

    def steps(self, story) -> None:
        fixture = seeded(story.app, owner_id=1)
        self.plans.first = fixture.plan.row_id
        self.supervisor_owner_environment = fixture.owner_environment.name
        opened = story.user_opens_in(self.supervisor_owner_environment, "/journal/plans")
        opened.expect_viewer_passed()
