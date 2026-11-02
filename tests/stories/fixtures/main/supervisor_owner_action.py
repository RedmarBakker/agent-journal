from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE
from journal.features.tasks.states.ready import Ready
from tests.in_process import posted
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture
from tests.test_supervisor_actions import _admitted_maintenance_context, maintenance_request
from tests.test_supervisor_authority import seeded


def prepare_owner_action(story):
    fixture = seeded(story.app)
    context = _admitted_maintenance_context(story.app, story.monkeypatch, fixture, "bounded_write")
    story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
    plan_id = fixture.plan.row_id
    with context["scope"].environment(fixture.owner_environment.row_id):
        before = context["maintenance"].plans.find(plan_id).priorities
    environment_name = fixture.owner_environment.name
    operation = {"kind": "plan_priorities", "plan_id": plan_id, "text": "Inspect the health check"}
    request = maintenance_request(context, [operation], "owner-undo-action")
    return {
        "context": context,
        "plan_id": plan_id,
        "environment_name": environment_name,
        "before": before,
        "owner_actor": fixture.owner,
        "request": request,
    }


def seed_owner_action(story, setup, tier):
    context, plan_id = setup["context"], setup["plan_id"]
    with story.monkeypatch.context() as patch:
        patch.setitem(CAPABILITY_CATALOGUE["Plans and tasks"]["plan"], "priorities", tier)
        story.viewer_status, story.viewer_answer = posted(
            story.app,
            "/_supervisor/v1/apply",
            setup["request"],
            {"X-Journal-Supervisor-Token": context["token"]},
        )
    story.observed(f"the supervisor records a {tier} plan priorities action", None, None)
    story.last_step.expect_viewer_passed()
    story.last_step.expect_viewer_part(("data", "command_receipts", 0, "tier"), tier)
    opened = story.user_opens_in(setup["environment_name"], "/journal/plans")
    opened.expect_viewer_passed()
    return {
        **setup,
        "receipt_id": story.viewer_answer["receipt_id"],
    }


class SupervisorOwnerActionSetup(StateFixture):
    """A plan owner is ready to check an undo receipt."""

    parent = WorkingAgent
    stack = (Ready,)

    def steps(self, story) -> None:
        self._owner_action_setup = prepare_owner_action(story)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)


class SupervisorOwnerAction(SupervisorOwnerActionSetup):
    """A plan owner has a recorded tier one supervisor action to undo."""

    parent = SupervisorOwnerActionSetup

    def steps(self, story) -> None:
        self._owner_action = seed_owner_action(story, self._owner_action_setup, "tier 1")

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
