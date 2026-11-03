from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.new_session import NewSession


class SupervisorOwnerPlanList(NewSession):
    """An owner has opened the plan list in a new session."""

    parent = NewSession

    def steps(self, story) -> None:
        opened = story.user_opens_in("main", "/journal/plans")
        opened.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
