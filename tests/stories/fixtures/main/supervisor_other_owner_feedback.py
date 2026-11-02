from journal.features.tasks.states.ready import Ready
from journal.repositories.environments import Environments
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.supervisor_authority import SUPERVISOR_ACTOR
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.supervisor_cost_data import record
from tests.stories.fixtures.supervisor.supervisor_grant_fixture import SupervisorGrantFixture
from tests.test_supervisor_authority import admitted, seeded


class SupervisorOtherOwnerFeedback(SupervisorGrantFixture):
    """A shared environment has a supervisor owned by someone else."""

    parent = NewSession

    def steps(self, story) -> None:
        self.restore_on(story)
        fixture = seeded(story.app, owner_id=2)
        grant, token, principal = admitted(fixture, "shadow")
        self.supervisor_credential = token
        self.plans.first = fixture.plan.row_id
        story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
        actor = Actor.plugin(SUPERVISOR_ACTOR)
        run_ref = "shared-feedback-run"
        with story.app.container.get(Scope).environment(PROJECT):
            entries = story.app.container.get(SupervisorEntries)
            record(story, entries, actor, principal, "SupervisorRun", "run", {
                "plan_id": grant["plan_id"], "run_ref": run_ref, "wakeup_id": run_ref,
                "kind": "scheduled", "source": "schedule", "observation_ids": [],
            })
            record(story, entries, actor, principal, "SupervisorActionReceipt", "receipt", {
                "plan_id": grant["plan_id"], "run_id": run_ref, "action_id": "shared-feedback-action",
                "status": "applied", "proposed_operations": [{"kind": "check_interval", "interval_minutes": 30}],
                "rationale": "The check has failed repeatedly.", "command_receipts": [],
            })
            record(story, entries, actor, principal, "SupervisorWakeup", "wakeup", {
                "plan_id": grant["plan_id"], "wakeup_id": run_ref, "kind": "scheduled",
                "result": "Acted", "skip_reason": "",
            })
        environment = story.app.container.get(Environments).find(fixture.plan.environment_id).name
        story.user_opens_in(environment, "/journal/supervisor/records?period=last_7_days").expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
