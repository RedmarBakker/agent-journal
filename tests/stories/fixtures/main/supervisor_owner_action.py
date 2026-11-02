from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE
from journal.features.tasks.states.ready import Ready
from tests.in_process import posted
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.state_fixture import StateFixture
from tests.test_supervisor_actions import _admitted_maintenance_context, maintenance_request
from tests.test_supervisor_authority import seeded


def seed_owner_action(story, tier):
    story.monkeypatch.setitem(CAPABILITY_CATALOGUE["Plans and tasks"]["plan"], "priorities", tier)
    fixture = seeded(story.app)
    context = _admitted_maintenance_context(story.app, story.monkeypatch, fixture, "bounded_write")
    story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
    plan_id = fixture.plan.row_id
    operation = {"kind": "plan_priorities", "plan_id": plan_id, "text": "Inspect the health check"}
    request = maintenance_request(context, [operation], "owner-undo-action")
    with context["scope"].environment(fixture.owner_environment.row_id):
        before = context["maintenance"].plans.find(plan_id).priorities
    story.viewer_status, story.viewer_answer = posted(
        story.app,
        "/_supervisor/v1/apply",
        request,
        {"X-Journal-Supervisor-Token": context["token"]},
    )
    story.observed("the supervisor records a plan priorities action", None, None)
    story.last_step.expect_viewer_passed()
    story.last_step.expect_viewer_part(("data", "command_receipts", 0, "tier"), tier)
    return {
        "plan_id": plan_id,
        "receipt_id": story.viewer_answer["receipt_id"],
        "environment_name": fixture.owner_environment.name,
        "before": before,
        "owner_actor": fixture.owner,
    }


class SupervisorOwnerAction(StateFixture):
    """A plan owner has a recorded supervisor plan-priorities action to undo."""

    parent = NewSession
    stack = (Ready,)

    def steps(self, story) -> None:
        self._owner_action = seed_owner_action(story, "tier 1")

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
    def before_priorities(self) -> str:
        return self._owner_action["before"]

    @property
    def owner_actor(self):
        return self._owner_action["owner_actor"]
