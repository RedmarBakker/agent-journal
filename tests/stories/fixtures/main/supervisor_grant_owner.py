from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.state_fixture import StateFixture
from tests.test_supervisor_authority import admitted, enrollment, seeded


class SupervisorGrantOwner(StateFixture):
    """The user owns a supervisor grant for a plan in their environment."""

    parent = NewSession

    def steps(self, story) -> None:
        fixture = seeded(story.app, owner_id=1)
        story.monkeypatch.setattr(type(fixture.authority.agents), "is_running", lambda _self, _environment: True)
        grant, token, _principal = admitted(fixture, "shadow")
        story.supervisor_credential = token
        story.supervisor_authority = fixture.authority
        story.supervisor_owner = fixture.owner
        self.plans.first = fixture.plan.row_id
        self.grants.first = grant["grant_id"]
        self.grants.replacement = enrollment(fixture, "bounded_write")
        story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
        result = story.user_opens_in(fixture.owner_environment.name, "/journal/supervisor/records?period=today")
        result.expect_viewer_passed()
        result.expect_viewer_part(("current", "runs"), 0)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
