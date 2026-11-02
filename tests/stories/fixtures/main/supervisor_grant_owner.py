from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.supervisor.supervisor_grant_fixture import SupervisorGrantFixture
from tests.test_supervisor_authority import admitted, enrollment, seeded


class SupervisorGrantOwner(SupervisorGrantFixture):
    """The user owns a supervisor grant for a plan in their environment."""

    parent = NewSession

    def steps(self, story) -> None:
        self.restore_on(story)
        fixture = seeded(story.app, owner_id=1)
        grant, token, _principal = admitted(fixture, "shadow")
        self.supervisor_credential = token
        self.supervisor_authority = fixture.authority
        self.supervisor_owner = fixture.owner
        self.supervisor_owner_environment = fixture.owner_environment.name
        self.supervisor_replacement = enrollment(fixture, "bounded_write")
        self.plans.first = fixture.plan.row_id
        self.supervisor_task_id = fixture.task.row_id
        self.grants.first = grant["grant_id"]
        story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
        result = story.user_opens_in(fixture.owner_environment.name, "/journal/supervisor/records?period=today")
        result.expect_viewer_passed()
        result.expect_viewer_part(("current", "runs"), 0)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
