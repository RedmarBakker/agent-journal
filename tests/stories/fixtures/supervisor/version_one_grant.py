from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.supervisor.supervisor_grant_fixture import SupervisorGrantFixture
from tests.test_supervisor_actions import maintenance_context


class VersionOneGrant(SupervisorGrantFixture):
    """An owner has enrolled a version 1 supervisor for a started plan with one active run."""

    parent = NewSession

    def steps(self, story) -> None:
        self.restore_on(story)
        context = maintenance_context(story.app, story.monkeypatch, "shadow")
        fixture = context["fixture"]
        self.plans.first = fixture.plan.row_id
        self.supervisor_credential = context["token"]
        story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
        result = story.user_opens_in(fixture.owner_environment.name, "/journal/plans")
        result.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
