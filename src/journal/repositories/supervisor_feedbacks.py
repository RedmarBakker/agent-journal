from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.features.plans.support.plan_owners import PlanOwners
from journal.models.entry import Entry
from journal.models.support.ref import Ref
from journal.models.supervisor_feedback import SupervisorFeedback
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource

FEEDBACK_ON = "feedback_on"
ACTION_RECEIPT = "SupervisorActionReceipt"
WAKEUP = "SupervisorWakeup"


class SupervisorFeedbacks(ScopedRepository[SupervisorFeedback]):
    model = SupervisorFeedback

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, time_source: TimeSource,
                 entries: Entries, links: Links, plans: Plans, owners: PlanOwners) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.entries, self.links, self.plans, self.owners = entries, links, plans, owners

    def create(self, plan_id: int, body: object, actor: Actor) -> SupervisorFeedback:
        owner = self._owner(plan_id, actor)
        if not isinstance(body, dict) or set(body) != {
            "decision_kind", "decision_id", "verdict", "comment", "correction", "scenario",
        }:
            raise Rejection("the supervisor feedback fields are invalid")
        feedback = self._feedback(body, plan_id)
        decision = self._decision(plan_id, owner, body["decision_kind"], body["decision_id"])
        with self.writing():
            saved = self.save(feedback, actor)
            self.links.linked(Ref.build(saved), Ref.build(decision), FEEDBACK_ON, actor)
        return saved

    def update(self, plan_id: int, feedback_id: int, body: object, actor: Actor) -> SupervisorFeedback:
        self._owner(plan_id, actor)
        row = self.find(feedback_id)
        if row.scenario.get("plan") != plan_id:
            raise Rejection("supervisor feedback is not available")
        if not isinstance(body, dict) or set(body) != {"verdict", "comment", "correction", "scenario"}:
            raise Rejection("the supervisor feedback fields are invalid")
        feedback = self._feedback(body, plan_id)
        return self.save(row.with_(
            verdict=feedback.verdict, comment=feedback.comment, correction=feedback.correction,
            scenario=feedback.scenario,
        ), actor)

    def for_plan(self, plan_id: int, actor: Actor) -> dict:
        owner = self._owner(plan_id, actor)
        rows = self.selected(self.query().filter_json("scenario->plan", plan_id).order_descending("id"))
        return {"plan_id": plan_id, "feedback": [self._present(row, plan_id, owner) for row in rows]}

    def _feedback(self, body: dict, plan_id: int) -> SupervisorFeedback:
        scenario = body["scenario"]
        if not isinstance(scenario, dict) or scenario.get("plan") != plan_id:
            raise Rejection("the supervisor feedback scenario plan must match the route")
        feedback = SupervisorFeedback(
            verdict=body["verdict"], comment=body["comment"], correction=body["correction"], scenario=scenario,
        )
        if refusal := feedback.refusal():
            raise Rejection(refusal)
        return feedback

    def _owner(self, plan_id: int, actor: Actor) -> int:
        plan = self.plans.find(plan_id)
        owner = self.owners.number(plan)
        if not actor.is_user() or not owner or actor.number() != owner:
            raise Rejection("only the plan owner may give or edit supervisor feedback")
        return owner

    def _decision(self, plan_id: int, owner: int, kind: object, decision_id: object) -> Entry:
        if not isinstance(kind, str):
            raise Rejection("the supervisor decision is not available")
        entry_type = {"action": ACTION_RECEIPT, "wakeup": WAKEUP}.get(kind)
        if entry_type is None or type(decision_id) is not int or decision_id < 1:
            raise Rejection("the supervisor decision is not available")
        rows = self.entries.selected_globally(
            self.entries.query().filter(id=decision_id, entry_type=entry_type).limit(1),
        )
        if not rows:
            raise Rejection("the supervisor decision is not available")
        entry = rows[0]
        tenant = f"owner:{owner}"
        if entry_type == ACTION_RECEIPT:
            scope = entry.data.get("scope", {})
            grant_id = entry.data.get("grant_id")
            grants = self.entries.selected_globally(
                self.entries.query().filter(entry_type="SupervisorGrant")
                .filter_json("data->grant_id", grant_id).order_descending("id").limit(1),
            ) if isinstance(grant_id, str) and grant_id else []
            matches = (
                scope.get("tenant_id") == tenant and bool(grants)
                and grants[0].data.get("owner_user_id") == owner
                and grants[0].data.get("plan_id") == plan_id
            )
        else:
            matches = entry.data.get("tenant_id") == tenant and entry.data.get("plan_id") == plan_id
        if not matches:
            raise Rejection("the supervisor decision is not available")
        return entry

    def _present(self, row: SupervisorFeedback, plan_id: int, owner: int) -> dict:
        targets = self.links.targets(row, FEEDBACK_ON)
        if len(targets) != 1 or targets[0].type != Entry.table():
            raise Rejection("the supervisor feedback decision is unavailable")
        decision = self._decision_for_ref(plan_id, owner, targets[0])
        return {
            "id": row.row_id,
            "verdict": row.verdict,
            "comment": row.comment,
            "correction": row.correction,
            "scenario": row.scenario,
            "creator": row.creator,
            "updater": row.updater,
            "decision": decision,
        }

    def _decision_for_ref(self, plan_id: int, owner: int, ref: Ref) -> dict:
        rows = self.entries.selected_globally(self.entries.query().filter(id=ref.id).limit(1))
        if not rows:
            raise Rejection("the supervisor feedback decision is unavailable")
        entry = rows[0]
        kind = "action" if entry.entry_type == ACTION_RECEIPT else "wakeup" if entry.entry_type == WAKEUP else ""
        if not kind:
            raise Rejection("the supervisor feedback decision is unavailable")
        self._decision(plan_id, owner, kind, entry.row_id)
        return {"kind": kind, "id": entry.row_id}
