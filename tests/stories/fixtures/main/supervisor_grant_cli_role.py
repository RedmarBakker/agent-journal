from journal.features.tasks.states.ready import Ready
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from tests.stories.fixtures.main.supervisor_grant_owner import SupervisorGrantOwner
from tests.stories.fixtures.state_fixture import StateFixture


class SupervisorGrantCliRole(StateFixture):
    """The supervisor has an active bounded-write grant for its plan."""

    parent = SupervisorGrantOwner

    def steps(self, story) -> None:
        grant, token = self.supervisor_authority.change(self.supervisor_owner, {
            "protocol_version": 1,
            "grant_id": story.grants.first,
            "expected_grant_version": 1,
            "change": {"kind": "replace", "enrollment": story.grants.replacement},
        })
        self.supervisor_credential = token
        authority = self.supervisor_authority
        credential = authority._credential_name(grant["grant_id"], grant["grant_version"])
        story.closers.append(lambda: authority.secrets_store.drop([credential]))
        self.supervisor_environment = story.app.container.get(Environments).find(grant["driver_environment_id"]).name

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


class SupervisorGrantCliReadOnly(StateFixture):
    """The supervisor has a grant with every writing capability switched off."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        enrollment = {
            **story.grants.replacement,
            "capabilities": {name: False for name in story.grants.replacement["capabilities"]},
        }
        grant, token = self.supervisor_authority.change(self.supervisor_owner, {
            "protocol_version": 1,
            "grant_id": story.grants.first,
            "expected_grant_version": 2,
            "change": {"kind": "replace", "enrollment": enrollment},
        })
        self.supervisor_credential = token
        authority = self.supervisor_authority
        credential = authority._credential_name(grant["grant_id"], grant["grant_version"])
        story.closers.append(lambda: authority.secrets_store.drop([credential]))

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


class SupervisorGrantUnwatchedPlan(StateFixture):
    """The supervisor has another started plan outside its watched plan list."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        environment = story.app.container.get(Environments).lookup(self.supervisor_environment)
        plans = story.app.container.get(Plans)
        scope = story.app.container.get(Scope)
        with scope.environment(environment.row_id):
            plan = plans.save(Plan(environment_id=environment.row_id, title="unwatched plan", state=PlanState.STARTED), self.supervisor_owner)
        self.plans.second = plan.row_id

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


class SupervisorGrantCliAlias(StateFixture):
    """The user has made an alias whose command is outside the supervisor grant."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        self.aliases.first = "unsafe"
        result = story.agent_runs(story.agents.main, f"alias add {self.aliases.first} 'task create outside grant'")
        result.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


class SupervisorGrantMutationAttempt(StateFixture):
    """The supervisor's active grant and stored credential are recorded before a grant mutation request."""

    parent = SupervisorGrantCliRole

    def steps(self, story) -> None:
        self.supervisor_entry_id_before = story.app.container.get(Entries).global_last_id()
        self.supervisor_secrets_before = self.supervisor_authority.secrets_store.values()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
