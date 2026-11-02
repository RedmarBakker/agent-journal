from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.environments import Environments
from journal.features.tasks.states.ready import Ready
from journal.support.actor import Actor
from journal.supervisor_authority import SUPERVISOR_ACTOR
from tests.stories.fixtures.main.supervisor_cost_data import record
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.supervisor.supervisor_grant_fixture import SupervisorGrantFixture
from tests.test_supervisor_authority import admitted, seeded


class SupervisorProposalHistory(SupervisorGrantFixture):
    """An owner has a current supervisor grant and one pending proposal."""

    parent = NewSession

    def steps(self, story) -> None:
        self.restore_on(story)
        fixture = seeded(story.app, owner_id=1)
        grant, token, principal = admitted(fixture, "shadow")
        self.supervisor_credential = token
        self.plans.first = fixture.plan.row_id
        story.closers.append(lambda: fixture.authority.secrets_store.drop(fixture.credentials))
        actor = Actor.plugin(SUPERVISOR_ACTOR)
        plan_id = grant["plan_id"]
        with story.app.container.get(Scope).environment(PROJECT):
            entries = story.app.container.get(SupervisorEntries)
            for name in ("first", "second"):
                run_ref = f"proposal-story-run-{name}"
                record(story, entries, actor, principal, "SupervisorRun", f"run:{name}", {
                    "plan_id": plan_id, "run_ref": run_ref, "wakeup_id": run_ref,
                    "kind": "scheduled", "source": "schedule", "observation_ids": [],
                })
                record(story, entries, actor, principal, "SupervisorActionReceipt", f"receipt:{name}", {
                    "plan_id": plan_id, "run_id": run_ref, "action_id": f"proposal-story-action-{name}",
                    "status": "proposed", "proposed_operations": [{"kind": "check_interval", "interval_minutes": 30}],
                    "rationale": "The check has failed repeatedly.", "command_receipts": [],
                })
                record(story, entries, actor, principal, "SupervisorWakeup", f"wakeup:{name}", {
                    "plan_id": plan_id, "wakeup_id": run_ref, "kind": "scheduled",
                    "result": "Proposed", "skip_reason": "",
                })
        environment = story.app.container.get(Environments).find(fixture.plan.environment_id).name
        story.user_opens_in(environment, "/journal/supervisor/records?period=last_7_days").expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
