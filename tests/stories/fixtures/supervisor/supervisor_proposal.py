from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from tests.stories.fixtures.supervisor.supervisor_grant_fixture import SupervisorGrantFixture
from tests.stories.fixtures.supervisor.supervisor_owner_plan_list import SupervisorOwnerPlanList
from tests.test_supervisor_actions import _admitted_maintenance_context, maintenance_request
from tests.test_supervisor_authority import seeded


class SupervisorProposal(SupervisorGrantFixture):
    """A shadow-mode supervisor has a current wake and one plan-priority operation."""

    parent = SupervisorOwnerPlanList

    def steps(self, story) -> None:
        self.restore_on(story)
        fixture = seeded(story.app, owner_id=1)
        context = _admitted_maintenance_context(story.app, story.monkeypatch, fixture, "shadow")
        operation = {
            "kind": "plan_priorities",
            "plan_id": context["grant"]["plan_id"],
            "text": "Review the failing check first",
        }
        self.supervisor_credential = context["token"]
        self.supervisor_plan = context["grant"]["plan_id"]
        self.supervisor_environment = story.app.container.get(Environments).find(
            fixture.owner_environment.row_id,
        ).name
        self.proposal_request = maintenance_request(context, [operation], "proposal-story")
        self.proposal_command = (
            f"plan priorities '{operation['text']}' --plan {self.supervisor_plan}"
        )
        self.proposal_wake_up = {
            "run_id": context["run"].data["run_ref"],
            "source": context["run"].data.get("source", ""),
        }
        self.proposal_rationale = self.proposal_request["rationale"]
        story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
        result = story.user_opens_in(self.supervisor_environment, "/journal/supervisor/history")
        result.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
