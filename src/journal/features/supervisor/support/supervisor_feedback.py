from typing import Any

from journal.features.supervisor.support.supervisor_record_reader import SupervisorRecordReader
from journal.models.entry import Entry
from journal.models.rule import Rule
from journal.repositories.entries import Entries
from journal.repositories.rules import Rules
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure

FEEDBACK_ENTRY = "SupervisorFeedback"
FEEDBACK_PAGE_SIZE = 100


class SupervisorFeedback:
    """Stores viewer feedback for a wake-up and lets its owner manage the resulting rules."""

    def __init__(self, authority: SupervisorAuthority, records: SupervisorRecordReader, entries: Entries,
                 control_entries: SupervisorEntries, rules: Rules, scope: Scope) -> None:
        self.authority, self.records, self.entries = authority, records, entries
        self.control_entries, self.rules, self.scope = control_entries, rules, scope

    def attach(self, answer: dict[str, Any]) -> dict[str, Any]:
        feedback = self._latest_feedback()
        history = [
            {**row, "feedback": self._public_feedback(feedback.get(row["id"]))}
            for row in answer["history"]
        ]
        return {**answer, "history": history}

    def save(self, history_id: int, body: object, actor: Actor) -> dict[str, Any]:
        self._user(actor)
        self._history_row(history_id)
        useful, comment, correction = self._feedback_fields(body)
        previous = self._latest_feedback().get(history_id)
        rule_id = previous.data.get("rule_id") if previous else None
        if rule_id and previous.data.get("correction") != correction:
            raise SupervisorFailure(409, "remove the narrowing rule before changing its correction")
        entry = self._record(history_id, {
            "useful": useful, "comment": comment, "correction": correction, "rule_id": rule_id,
        }, actor)
        return {"feedback": self._public_feedback(entry)}

    def make_rule(self, history_id: int, actor: Actor) -> dict[str, Any]:
        self._owner(actor)
        history = self._history_row(history_id)
        feedback = self._latest_feedback().get(history_id)
        if feedback is None or not feedback.data.get("correction"):
            raise SupervisorFailure(409, "save a correction before turning it into a rule")
        rule_id = feedback.data.get("rule_id")
        if type(rule_id) is int:
            rule = self._rule(rule_id)
            if rule:
                return {"rule": self._public_rule(rule, history_id)}
            raise SupervisorFailure(409, "the correction's rule is no longer available")
        rule = self.rules.save(self._narrowing_rule(history, feedback.data["correction"]).person_created(), actor)
        entry = self._record(history_id, {
            **self._feedback_data(feedback), "rule_id": rule.row_id,
        }, actor)
        return {"rule": self._public_rule(rule, entry.data["history_id"])}

    def owner_rules(self, actor: Actor) -> list[dict[str, Any]]:
        self._owner(actor)
        rules = []
        for history_id, feedback in self._latest_feedback().items():
            rule_id = feedback.data.get("rule_id")
            rule = self._rule(rule_id) if type(rule_id) is int else None
            if rule:
                rules.append(self._public_rule(rule, history_id))
        return sorted(rules, key=lambda rule: rule["id"])

    def remove_rule(self, rule_id: int, actor: Actor) -> dict[str, int]:
        self._owner(actor)
        feedback = next((entry for entry in self._latest_feedback().values()
                         if entry.data.get("rule_id") == rule_id), None)
        rule = self._rule(rule_id)
        if feedback is None or rule is None:
            raise SupervisorFailure(404, "the supervisor rule is not available")
        self.rules.delete(rule, actor)
        self._record(feedback.data["history_id"], {
            **self._feedback_data(feedback), "rule_id": None,
        }, actor)
        return {"removed": rule_id}

    def _history_row(self, history_id: int) -> dict[str, Any]:
        if history_id < 1:
            raise SupervisorFailure(400, "the supervisor history row is invalid")
        row = self.records.history_row(history_id)
        if row is None:
            raise SupervisorFailure(404, "the supervisor history row is not available")
        return row

    def _owner(self, actor: Actor) -> None:
        self.authority.owner_control(actor, self.scope.id)

    @staticmethod
    def _user(actor: Actor) -> None:
        if not actor.is_user():
            raise SupervisorFailure(403, "supervisor feedback is available to people in the current environment")

    @staticmethod
    def _feedback_fields(body: object) -> tuple[bool, str, str]:
        if (not isinstance(body, dict) or set(body) != {"useful", "comment", "correction"}
                or type(body["useful"]) is not bool
                or not isinstance(body["comment"], str) or len(body["comment"]) > 4000
                or not isinstance(body["correction"], str) or len(body["correction"]) > 4000):
            raise SupervisorFailure(400, "the supervisor feedback is invalid")
        return body["useful"], body["comment"], body["correction"]

    def _latest_feedback(self) -> dict[int, Entry]:
        environment_id = self.scope.id
        with self.scope.environment(PROJECT):
            entries = []
            after_id = 0
            while True:
                page = self.entries.supervisor_page(
                    FEEDBACK_ENTRY, FEEDBACK_PAGE_SIZE, after_id, environment_id=environment_id,
                )
                entries.extend(page)
                if len(page) < FEEDBACK_PAGE_SIZE:
                    break
                after_id = page[-1].row_id
        latest = {}
        for entry in entries:
            history_id = entry.data.get("history_id")
            if type(history_id) is int:
                latest[history_id] = entry
        return latest

    @staticmethod
    def _public_feedback(entry: Entry | None) -> dict[str, Any]:
        if entry is None:
            return {"useful": None, "comment": "", "correction": "", "rule_id": None}
        return {
            "useful": entry.data.get("useful"), "comment": entry.data.get("comment", ""),
            "correction": entry.data.get("correction", ""), "rule_id": entry.data.get("rule_id"),
        }

    @staticmethod
    def _feedback_data(entry: Entry) -> dict[str, Any]:
        return {key: entry.data.get(key) for key in ("useful", "comment", "correction")}

    def _record(self, history_id: int, feedback: dict[str, Any], actor: Actor) -> Entry:
        latest = self._latest_feedback().get(history_id)
        revision = latest.data.get("revision", 0) + 1 if latest else 1
        environment_id = self.scope.id
        with self.scope.environment(PROJECT):
            return self.control_entries.recorded(Entry(
                environment_id=PROJECT,
                entry_type=FEEDBACK_ENTRY,
                actor=actor,
                data={"environment_id": environment_id, "history_id": history_id,
                      "revision": revision, **feedback},
                idempotency=f"supervisor:feedback:{environment_id}:{history_id}:{revision}",
            ), actor)

    def _narrowing_rule(self, history: dict[str, Any], correction: str) -> Rule:
        areas = list(dict.fromkeys(action["area"] for action in history["actions"]))
        plan_id = history["plan_id"]
        scope = f"Plan {plan_id}" if type(plan_id) is int else "the whole environment"
        scope += f" in {', '.join(areas)}" if areas else " across the whole environment"
        keywords = ["supervisor"]
        if type(plan_id) is int:
            keywords.append(f"plan-{plan_id}")
        keywords.extend(dict.fromkeys(action["area_key"] for action in history["actions"]))
        return Rule(
            text=f"For the supervisor's decisions about {scope}: {correction}",
            reason=f"Correction to supervisor wake-up {history['id']}.",
            keywords=tuple(keywords),
        )

    def _rule(self, rule_id: int) -> Rule | None:
        rows = self.rules.all_matching(id=rule_id)
        return rows[0] if rows else None

    @staticmethod
    def _public_rule(rule: Rule, history_id: int) -> dict[str, Any]:
        return {"id": rule.row_id, "text": rule.text, "reason": rule.reason, "history_id": history_id}
