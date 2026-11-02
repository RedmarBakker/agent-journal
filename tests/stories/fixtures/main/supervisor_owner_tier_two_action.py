from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.supervisor_owner_action import SupervisorOwnerActionSetup
from tests.in_process import posted
from tests.test_supervisor_actions import _admitted_maintenance_context, maintenance_request
from tests.test_supervisor_authority import seeded


class SupervisorOwnerTierTwoAction(StateFixture):
    """A plan owner has a recorded supervisor plan tell action at tier 2."""

    parent = SupervisorOwnerActionSetup

    def steps(self, story) -> None:
        fixture = seeded(story.app)
        context = _admitted_maintenance_context(
            story.app, story.monkeypatch, fixture, "bounded_write",
            capability_decisions={"plan tell": "may_act"},
        )
        story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
        operation = {"kind": "plan_tell", "plan_id": context["grant"]["plan_id"],
                     "text": "Review the failed check first"}
        request = maintenance_request(context, [operation], "owner-undo-tier-two-action")
        story.viewer_status, story.viewer_answer = posted(
            story.app, "/_supervisor/v1/apply", request,
            {"X-Journal-Supervisor-Token": context["token"]},
        )
        story.observed("the supervisor tells the plan agent with a tier 2 command", None, None)
        story.last_step.expect_viewer_passed()
        story.last_step.expect_viewer_part(("data", "status"), "applied")
        story.last_step.expect_viewer_part(("data", "command_receipts", 0, "command"), "plan tell")
        story.last_step.expect_viewer_part(("data", "command_receipts", 0, "tier"), "tier 2")
        self._owner_action = {
            "plan_id": context["grant"]["plan_id"],
            "receipt_id": story.viewer_answer["receipt_id"],
            "environment_name": fixture.owner_environment.name,
            "owner_actor": fixture.owner,
        }

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)

    def copied(self):
        copy = super().copied()
        copy._owner_action = self._owner_action
        return copy

    @property
    def plan_id(self) -> int:
        return self._owner_action["plan_id"]

    @property
    def receipt_id(self) -> int:
        return self._owner_action["receipt_id"]

    @property
    def environment_name(self) -> str:
        return self._owner_action["environment_name"]

    @property
    def owner_actor(self):
        return self._owner_action["owner_actor"]
