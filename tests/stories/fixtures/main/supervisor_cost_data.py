from journal.models.entry import Entry
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SUPERVISOR_ACTOR


def add_run(story, principal, plan_id: int, name: str, at: float,
            cost: str | None, kinds: tuple[str, ...], useful: bool = False) -> int:
    actor = Actor.plugin(SUPERVISOR_ACTOR)
    entries = story.app.container.get(SupervisorEntries)
    story.app.container.get(TimeSource).pin(at)
    run_ref = f"cost-{name}"
    common = {"plan_id": plan_id, "run_ref": run_ref, "wakeup_id": run_ref,
              "kind": "scheduled", "source": "schedule", "observation_ids": []}
    record(story, entries, actor, principal, "SupervisorRun", f"run:{name}", common)
    operations = [{"kind": kind, "interval_minutes": 30} for kind in kinds]
    commands = [
        {"area": "Checks" if kind == "check_interval" else "Plans and tasks",
         "tier": "tier 1", "status": "applied", "readback_verification": "verified",
         "rows_changed": []}
        for kind in kinds
    ]
    receipt = record(story, entries, actor, principal, "SupervisorActionReceipt", f"receipt:{name}", {
        "plan_id": plan_id, "run_id": run_ref, "action_id": run_ref, "status": "applied",
        "proposed_operations": operations, "command_receipts": commands, "changes": [],
    })
    record(story, entries, actor, principal, "SupervisorWakeup", f"wakeup:{name}", {
        "plan_id": plan_id, "wakeup_id": run_ref, "kind": "scheduled", "result": "Acted",
        "skip_reason": "",
    })
    if cost is not None:
        record(story, entries, actor, principal, "SupervisorUsage", f"usage:{name}", {
            "run_ref": run_ref, "cost_usd": cost, "status": "known",
        })
    if useful:
        record(story, entries, actor, principal, "SupervisorActionReport", f"useful:{name}", {
            "plan_id": plan_id, "receipt_id": receipt.row_id,
            "report_kind": "outcome", "outcome": "useful_evidence",
        })
    return receipt.row_id


def add_quiet(story, principal, plan_id: int, name: str, at: float) -> None:
    story.app.container.get(TimeSource).pin(at)
    record(story, story.app.container.get(SupervisorEntries), Actor.plugin(SUPERVISOR_ACTOR), principal,
           "SupervisorWakeup", f"quiet:{name}", {
               "plan_id": plan_id, "wakeup_id": f"quiet-{name}", "kind": "failed_check",
               "result": "Skipped as quiet", "skip_reason": "quiet",
           })


def record(story, entries, actor: Actor, principal, entry_type: str, suffix: str, data: dict) -> Entry:
    with story.app.container.get(Scope).environment(PROJECT):
        return entries.recorded(Entry(
            environment_id=PROJECT,
            entry_type=entry_type,
            actor=actor,
            data={"tenant_id": principal.scope["tenant_id"], "grant_id": principal.grant_id,
                  "grant_version": principal.grant_version, **data},
            idempotency=f"story:supervisor-costs:{principal.grant_id}:{suffix}",
        ), actor)
