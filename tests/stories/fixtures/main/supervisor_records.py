from journal.features.tasks.states.ready import Ready
from journal.models.entry import Entry
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SUPERVISOR_ACTOR, SupervisorAuthority
from tests.agent_hooks import story_seconds
from tests.stories.fixtures.supervisor.version_one_grant import VersionOneGrant


class SupervisorRecords(VersionOneGrant):
    """A version 1 supervisor has runs and receipts in current and previous periods."""

    parent = VersionOneGrant

    def steps(self, story) -> None:
        plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
        authority = story.app.container.get(SupervisorAuthority)
        principal = authority.authenticate(self.supervisor_credential)
        foreign_environment = story.app.container.get(Environments).made(f"supervisor-private-{plan.row_id}", Actor.user(2))
        with story.app.container.get(Scope).environment(foreign_environment.row_id):
            foreign = story.app.container.get(Plans).save(
                Plan(title="private plan", brief="private work", state=PlanState.STARTED, mode=PlanMode.SOLO),
                Actor.user(2),
            )
        self.plans.foreign = foreign.row_id
        now = story_seconds(story.app)
        source = story.app.container.get(TimeSource)
        entries = story.app.container.get(SupervisorEntries)
        actor = Actor.plugin(SUPERVISOR_ACTOR)
        with story.app.container.get(Scope).environment(PROJECT):
            source.pin(now - 8 * 24 * 60 * 60)
            self.add_receipts(story, entries, actor, principal, plan.row_id, "previous", 2, ("applied", "proposed"), "check_interval", 1)
            source.pin(now - 24 * 60 * 60)
            self.add_receipts(story, entries, actor, principal, plan.row_id, "current-check", 102,
                              ("applied",) * 51 + ("conflicted",) * 17 + ("proposed",) * 17 + ("rejected",) * 17,
                              "check_interval", 30)
            self.add_receipts(story, entries, actor, principal, plan.row_id, "current-plan", 2,
                              ("applied",), "diagnostic_task", 0)
        source.pin(now)
        result = story.user_opens_in(
            story.app.container.get(Environments).find(plan.environment_id).name,
            f"/journal/supervisor/records?period=last_7_days&plan_id={plan.row_id}",
        )
        result.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)

    def add_receipts(self, story, entries, actor, principal, plan_id: int, prefix: str, count: int,
                     statuses: tuple[str, ...], operation: str, verified: int) -> None:
        for index in range(count):
            run_ref = f"{prefix}-{index}"
            self.record(entries, actor, "SupervisorRun", principal, f"run:{run_ref}", {
                "plan_id": plan_id, "run_ref": run_ref, "source": "timer", "status": "complete",
            })
            status = statuses[index] if len(statuses) == count else statuses[min(index * len(statuses) // count, len(statuses) - 1)]
            receipt = self.record(entries, actor, "SupervisorActionReceipt", principal, f"receipt:{run_ref}", {
                "run_id": run_ref, "action_id": f"action-{run_ref}", "status": status,
                "proposed_operations": [{"kind": operation}], "reason": "",
            })
            if index < verified:
                self.record(entries, actor, "SupervisorActionReport", principal, f"verification:{run_ref}", {
                    "plan_id": plan_id, "run_id": run_ref, "receipt_id": receipt.row_id,
                    "report_kind": "verification", "verification": "verified",
                })

    @staticmethod
    def record(entries, actor: Actor, entry_type: str, principal, suffix: str, data: dict) -> Entry:
        return entries.recorded(Entry(
            environment_id=PROJECT,
            entry_type=entry_type,
            actor=actor,
            data={"tenant_id": principal.scope["tenant_id"], "grant_id": principal.grant_id,
                  "grant_version": principal.grant_version, **data},
            idempotency=f"story:supervisor-records:{principal.grant_id}:{suffix}",
        ), actor)
