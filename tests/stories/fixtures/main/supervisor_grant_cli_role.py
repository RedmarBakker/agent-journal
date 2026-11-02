from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from tests.stories.fixtures.main.supervisor_grant_owner import SupervisorGrantOwner


class SupervisorGrantCliRole(SupervisorGrantOwner):
    """The supervisor has an active bounded-write grant for its plan."""

    parent = SupervisorGrantOwner

    def steps(self, story) -> None:
        result = story.user_presses_with_headers("/_supervisor/v1/enrollment/change", {
            "protocol_version": 1,
            "grant_id": story.grants.first,
            "expected_grant_version": 1,
            "change": {"kind": "replace", "enrollment": self.supervisor_replacement},
        })
        result.expect_viewer_passed()
        grant = story.viewer_answer["body"]
        self.supervisor_credential = story.viewer_answer["headers"]["X-Journal-Supervisor-Token"]
        authority = self.supervisor_authority
        credential = authority._credential_name(grant["grant_id"], grant["grant_version"])
        story.closers.append(lambda: authority.secrets_store.drop([credential]))
        self.supervisor_environment = story.app.container.get(Environments).find(grant["driver_environment_id"]).name

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


class SupervisorGrantCliProposalOnly(SupervisorGrantCliRole):
    """The supervisor grant can propose but cannot apply changes."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        enrollment = {
            **self.supervisor_replacement,
            "mode": "shadow",
        }
        result = story.user_presses_with_headers("/_supervisor/v1/enrollment/change", {
            "protocol_version": 1,
            "grant_id": story.grants.first,
            "expected_grant_version": 2,
            "change": {"kind": "replace", "enrollment": enrollment},
        })
        result.expect_viewer_passed()
        grant = story.viewer_answer["body"]
        self.supervisor_credential = story.viewer_answer["headers"]["X-Journal-Supervisor-Token"]
        authority = self.supervisor_authority
        credential = authority._credential_name(grant["grant_id"], grant["grant_version"])
        story.closers.append(lambda: authority.secrets_store.drop([credential]))

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


class SupervisorGrantCliAlias(SupervisorGrantCliRole):
    """The user has made an alias whose command is outside the supervisor grant."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        self.aliases.first = "unsafe"
        result = story.agent_runs(story.agents.main, f"alias add {self.aliases.first} 'task create outside grant'")
        result.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


