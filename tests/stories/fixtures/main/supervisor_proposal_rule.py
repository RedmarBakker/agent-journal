from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.state_fixture import StateFixture
from tests.test_supervisor_actions import maintenance_context


class SupervisorProposalRule(StateFixture):
    """The owner has limited plan priorities to proposals on the active supervisor grant."""

    parent = NewSession
    stack = (Ready,)

    def steps(self, story) -> None:
        context = maintenance_context(
            story.app, story.monkeypatch, rules=[{"command": "plan priorities", "effect": "propose"}],
        )
        story.observed("the owner limits plan priorities to proposals", None, None)
        self._context = context
        self.supervisor_credential = context["token"]
        story.plans.first = context["grant"]["plan_id"]
        story.grants.first = context["grant"]["grant_id"]
        story.closers.append(lambda: context["fixture"].authority.secrets_store.drop(context["fixture"].credentials))

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)

    @property
    def context(self) -> dict:
        return self._context
