import json
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from hashlib import sha256
from secrets import token_urlsafe

from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.repositories.scope import PROJECT
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor


MAX_RETRIES = 2
MAX_DAILY_RUNS = 100
MAX_INTENT_BYTES = 32_000
MAX_IDENTIFIER_BYTES = 256
MAX_OBSERVATION_AGE = 600
DEFAULT_LEASE_SECONDS = 300
MONEY_UNIT = Decimal("0.000001")
MILLION = Decimal("1000000")
TERMINAL_RUN_STATES = ("complete", "conflicted", "rejected")


def digest(value: str) -> str:
    return sha256(value.encode()).hexdigest()


def canonical(value: object) -> str | None:
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=False)
        encoded = text.encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError):
        return None
    return text if len(encoded) <= MAX_INTENT_BYTES else None


def parsed_time(value: object) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
    else:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def positive_decimal(value: object) -> Decimal | None:
    parsed = decimal_amount(value)
    return parsed if parsed is not None and parsed > 0 else None


def decimal_amount(value: object) -> Decimal | None:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return parsed if parsed.is_finite() and parsed >= 0 else None


def cost(input_tokens: int, output_tokens: int, input_rate: Decimal, output_rate: Decimal) -> Decimal:
    total = (Decimal(input_tokens) * input_rate + Decimal(output_tokens) * output_rate) / MILLION
    return total.quantize(MONEY_UNIT, rounding=ROUND_CEILING)


def action_receipt_key(tenant_id: str, action_id: str) -> str:
    return supervisor_key("action-receipt", tenant_id, action_id)


def action_reuse_key(tenant_id: str, action_id: str, intent_hash: str) -> str:
    return supervisor_key("action-reuse", tenant_id, action_id, intent_hash)


def supervisor_key(kind: str, *parts: str) -> str:
    return f"supervisor:{kind}:{digest(canonical(parts) or '')}"


class SupervisorAdmissions:
    """Claims fenced supervisor runs and applies their journal-owned action receipts."""

    def __init__(
        self,
        entries: Entries,
        control_entries: SupervisorEntries,
        prices: Mapping[str, tuple[object, object]],
        clock: Callable[[], datetime],
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
    ) -> None:
        if not 1 <= lease_seconds <= 600:
            raise ValueError("supervisor leases must be between 1 and 600 seconds")
        self.entries = entries
        self.control_entries = control_entries
        self.prices = prices
        self.clock = clock
        self.lease_seconds = lease_seconds

    def start_installation(self, credential: str, installation_id: str) -> dict:
        if not self._identifier(installation_id):
            return self._result("rejected", "installation_id_invalid")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            context = self._credential(credential)
            if context is None:
                return self._result("rejected", "credential_unknown")
            if context[3]:
                return self._result("rejected", context[3])
            _, grant, tenant_id, _ = context
            key = self._key("installation", tenant_id, installation_id)
            if prior := self.entries.keyed(key):
                return self._record_result(prior[0])
            latest = self.entries.supervisor_records("SupervisorInstallation", last=1, tenant_id=tenant_id)
            prior_epoch = integer(latest[0].data.get("epoch")) if latest else 0
            if prior_epoch is None:
                return self._result("rejected", "installation_epoch_invalid")
            epoch = prior_epoch + 1
            row = self._record("SupervisorInstallation", key, tenant_id, {"tenant_id": tenant_id, "grant_id": grant["grant_id"], "installation_id": installation_id, "epoch": epoch})
            return self._record_result(row)

    def admit_run(self, credential: str, installation_epoch: int, source: str, event_id: str, observation: Mapping[str, object]) -> dict:
        if integer(installation_epoch) in (None, 0) or not self._identifier(event_id) or source not in ("hook", "timer") or not isinstance(observation, Mapping):
            return self._result("skip", "invalid_trigger")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            context = self._credential(credential)
            if context is None:
                return self._result("rejected", "credential_unknown")
            _, grant, tenant_id, reason = context
            if reason:
                return self._result("rejected", reason)
            now = self._now()
            installation = self._installation(tenant_id)
            if installation is None or installation["epoch"] != installation_epoch:
                return self._result("skip", "stale_installation_epoch")
            if reason := self._observation_reason(grant, observation, now):
                return self._result("skip", reason)
            model = grant.get("model", "")
            rates = self._rates(model)
            if rates is None:
                return self._result("skip", "unknown_model_price")
            reservation = self._reservation(grant, rates)
            if reservation is None:
                return self._result("skip", "unknown_budget")
            plan_id, node_id = grant["plan_id"], grant["node_id"]
            episode_id, fingerprint = observation["episode_id"], observation["problem_fingerprint"]
            evidence_generation = integer(observation["evidence_generation"])
            if not self._identifier(episode_id) or not self._identifier(fingerprint) or evidence_generation is None:
                return self._result("skip", "invalid_episode")
            episode_intent = {"tenant_id": tenant_id, "plan_id": plan_id, "episode_id": episode_id, "problem_fingerprint": fingerprint, "evidence_generation": evidence_generation}
            episode_text = canonical(episode_intent)
            if episode_text is None:
                return self._result("skip", "invalid_episode")
            episode_key = self._key("episode", tenant_id, plan_id, episode_id)
            if prior := self.entries.keyed(episode_key):
                if prior[0].data.get("intent") != episode_text:
                    return self._result("rejected", "episode_id_reused")
            else:
                self._record("SupervisorEpisode", episode_key, tenant_id, {"tenant_id": tenant_id, **episode_intent, "intent": episode_text})
            run_intent = {"episode": episode_intent, "source": source, "event_id": event_id, "epoch": installation_epoch, "observation": dict(observation), "model": model, "reservation": reservation}
            run_text = canonical(run_intent)
            if run_text is None:
                return self._result("skip", "invalid_run_intent")
            run_key = self._key("run", tenant_id, plan_id, node_id, source, event_id)
            if prior := self.entries.keyed(run_key):
                if prior[0].data.get("intent") != run_text:
                    return self._result("rejected", "event_id_reused")
                return self._record_result(prior[0], duplicate=True)
            if self._active_run(tenant_id, plan_id, node_id, installation_epoch, now):
                return self._result("skip", "overlapping_run")
            if not self._budget_available(tenant_id, grant, reservation, now.date().isoformat()):
                return self._result("skip", "budget_exhausted")
            latest = self._latest_run(tenant_id, plan_id, node_id)
            latest_fence = integer(latest.data.get("fence")) if latest else 0
            if latest_fence is None:
                return self._result("skip", "fence_invalid")
            fence = latest_fence + 1
            run_ref = token_urlsafe(32)
            row = self._record("SupervisorRun", run_key, tenant_id, {
                "tenant_id": tenant_id,
                "grant_id": grant["grant_id"],
                "grant_version": grant["version"],
                "plan_id": plan_id,
                "node_id": node_id,
                "episode_id": episode_id,
                "source": source,
                "event_id": event_id,
                "installation_epoch": installation_epoch,
                "fence": fence,
                "run_ref": run_ref,
                "lease_until": (now + timedelta(seconds=self.lease_seconds)).isoformat(),
                "day": now.date().isoformat(),
                "model": model,
                "reservation": reservation,
                "max_retries": reservation["max_retries"],
                "status": "admitted",
                "intent": run_text,
            })
            return self._record_result(row)

    def begin_run(self, credential: str, run_ref: str, fence: int) -> dict:
        if not self._identifier(run_ref) or integer(fence) is None or fence == 0:
            return self._result("rejected", "run_reference_invalid")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            context = self._credential(credential)
            if context is None:
                return self._result("rejected", "credential_unknown")
            if context[3]:
                return self._result("rejected", context[3])
            _, grant, tenant_id, _ = context
            run = self._run(tenant_id, run_ref)
            if reason := self._run_reason(grant, run, fence, self._now()):
                return self._result("conflicted", reason)
            prior = self.entries.keyed(self._run_state_key(tenant_id, run_ref, "start"))
            if prior:
                return self._record_result(prior[0], duplicate=True)
            row = self._record("SupervisorRunState", self._run_state_key(tenant_id, run_ref, "start"), tenant_id, {"tenant_id": tenant_id, "run_ref": run_ref, "fence": fence, "status": "pending", "retry_count": 0})
            return self._record_result(row)

    def retry_run(self, credential: str, run_ref: str, fence: int, retry_id: str) -> dict:
        if not self._identifier(run_ref) or integer(fence) is None or fence == 0 or not self._identifier(retry_id):
            return self._result("rejected", "retry_id_invalid")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            context = self._credential(credential)
            if context is None:
                return self._result("rejected", "credential_unknown")
            if context[3]:
                return self._result("rejected", context[3])
            _, grant, tenant_id, _ = context
            key = self._run_state_key(tenant_id, run_ref, retry_id)
            if prior := self.entries.keyed(key):
                return self._record_result(prior[0], duplicate=True) if prior[0].data.get("fence") == fence else self._result("rejected", "retry_id_reused")
            run = self._run(tenant_id, run_ref)
            if reason := self._run_reason(grant, run, fence, self._now()):
                return self._result("conflicted", reason)
            latest = self._latest_run_state(tenant_id, run_ref)
            retries = latest.data["retry_count"] if latest else 0
            if retries >= run.data["max_retries"]:
                return self._result("rejected", "retry_limit_exhausted")
            row = self._record("SupervisorRunState", key, tenant_id, {"tenant_id": tenant_id, "run_ref": run_ref, "fence": fence, "status": "pending", "retry_count": retries + 1, "retry_id": retry_id})
            return self._record_result(row)

    def record_usage(self, run_ref: str, usage: Mapping[str, object] | None) -> dict:
        if not self._identifier(run_ref):
            return self._result("rejected", "run_unknown")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            runs = self.entries.supervisor_records("SupervisorRun", last=1, run_ref=run_ref)
            if not runs:
                return self._result("rejected", "run_unknown")
            run = runs[0]
            known_key = self._usage_key(run.data["tenant_id"], run_ref)
            if not isinstance(usage, Mapping):
                if known := self.entries.keyed(known_key):
                    return self._record_result(known[0], duplicate=True)
                row = self._record("SupervisorUsage", self._usage_pending_key(run.data["tenant_id"], run_ref), run.data["tenant_id"], {"tenant_id": run.data["tenant_id"], "run_ref": run_ref, "status": "pending", "reason": "usage_unknown"})
                return self._record_result(row)
            turns = integer(usage.get("turns"))
            input_tokens = integer(usage.get("input_tokens"))
            output_tokens = integer(usage.get("output_tokens"))
            if turns is None or input_tokens is None or output_tokens is None or turns == 0:
                if known := self.entries.keyed(known_key):
                    return self._record_result(known[0], duplicate=True)
                row = self._record("SupervisorUsage", self._usage_pending_key(run.data["tenant_id"], run_ref), run.data["tenant_id"], {"tenant_id": run.data["tenant_id"], "run_ref": run_ref, "status": "pending", "reason": "usage_unknown"})
                return self._record_result(row)
            reservation = run.data["reservation"]
            input_rate = positive_decimal(reservation["input_rate_per_million"])
            output_rate = positive_decimal(reservation["output_rate_per_million"])
            if input_rate is None or output_rate is None:
                return self._result("rejected", "unknown_model_price")
            actual_cost = cost(input_tokens, output_tokens, input_rate, output_rate)
            overrun = turns > reservation["turns"] or input_tokens > reservation["input_tokens"] or output_tokens > reservation["output_tokens"] or actual_cost > Decimal(reservation["cost_usd"])
            data = {"tenant_id": run.data["tenant_id"], "run_ref": run_ref, "turns": turns, "input_tokens": input_tokens, "output_tokens": output_tokens, "cost_usd": str(actual_cost), "overrun": overrun}
            intent = canonical(data)
            if prior := self.entries.keyed(known_key):
                if prior[0].data.get("intent") != intent:
                    return self._result("rejected", "usage_id_reused", run_ref=run_ref)
                return self._record_result(prior[0], duplicate=True)
            row = self._record("SupervisorUsage", known_key, run.data["tenant_id"], {**data, "intent": intent, "status": "overrun" if overrun else "known"})
            return self._record_result(row)

    def finish_run(self, credential: str, run_ref: str, fence: int) -> dict:
        if not self._identifier(run_ref) or integer(fence) is None or fence == 0:
            return self._result("rejected", "run_reference_invalid")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            context = self._credential(credential)
            if context is None:
                return self._result("rejected", "credential_unknown")
            if context[3]:
                return self._result("rejected", context[3])
            _, grant, tenant_id, _ = context
            run = self._run(tenant_id, run_ref)
            if reason := self._run_reason(grant, run, fence, self._now()):
                return self._result("conflicted", reason)
            key = self._run_state_key(tenant_id, run_ref, "complete")
            if prior := self.entries.keyed(key):
                return self._record_result(prior[0], duplicate=True)
            latest = self._latest_run_state(tenant_id, run_ref)
            retries = latest.data["retry_count"] if latest else 0
            row = self._record("SupervisorRunState", key, tenant_id, {"tenant_id": tenant_id, "run_ref": run_ref, "fence": fence, "status": "complete", "retry_count": retries})
            return self._record_result(row)

    def admit_action(self, credential: str, run_ref: str, fence: int, action_id: str, intent: Mapping[str, object]) -> dict:
        if not self._identifier(run_ref) or integer(fence) is None or fence == 0 or not self._identifier(action_id):
            return self._result("rejected", "action_id_invalid")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            context = self._credential(credential)
            if context is None:
                return self._result("rejected", "credential_unknown")
            _, grant, tenant_id, credential_reason = context
            normalized, intent_hash = self._intent(intent)
            if normalized is None:
                return self._result("rejected", "invalid_action_intent")
            receipt_key = self._action_receipt_key(tenant_id, action_id)
            if prior := self.entries.keyed(receipt_key):
                return self._prior_action(prior[0], intent_hash, tenant_id, action_id)
            action_key = self._action_key(tenant_id, action_id)
            if prior := self.entries.keyed(action_key):
                if prior[0].data.get("intent_hash") != intent_hash:
                    return self._reused_action(tenant_id, action_id, normalized, intent_hash)
                if prior[0].data.get("run_ref") != run_ref or prior[0].data.get("fence") != fence:
                    return self._result("rejected", "action_admission_mismatch")
                return self._record_result(prior[0], duplicate=True)
            if credential_reason:
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, "rejected", credential_reason, {}, Actor.system())
            pending_key = self._action_state_key(tenant_id, action_id, "usage-pending")
            if pending := self.entries.keyed(pending_key):
                if pending[0].data.get("intent_hash") != intent_hash:
                    return self._reused_action(tenant_id, action_id, normalized, intent_hash)
                if pending[0].data.get("run_ref") != run_ref or pending[0].data.get("fence") != fence:
                    return self._result("rejected", "action_admission_mismatch")
            run = self._run(tenant_id, run_ref)
            if reason := self._action_reason(grant, run, fence, normalized, self._now()):
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, "rejected", reason, {}, self._actor(tenant_id))
            usage_reason = self._usage_reason(tenant_id, run_ref)
            if usage_reason == "usage_unknown":
                row = self._record("SupervisorActionState", pending_key, tenant_id, {"tenant_id": tenant_id, "action_id": action_id, "run_ref": run_ref, "fence": fence, "intent_hash": intent_hash, "status": "pending", "reason": usage_reason, "retry_count": self._retry_count(tenant_id, run_ref)})
                return self._record_result(row)
            if usage_reason:
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, "rejected", usage_reason, {}, self._actor(tenant_id))
            row = self._record("SupervisorAction", action_key, tenant_id, {"tenant_id": tenant_id, "action_id": action_id, "run_ref": run_ref, "fence": fence, "intent": normalized, "intent_hash": intent_hash, "status": "admitted"})
            return self._record_result(row)

    def apply_action(self, credential: str, run_ref: str, fence: int, action_id: str, intent: Mapping[str, object], validate: Callable[[dict, dict, dict], dict | None], operation: Callable[[dict, Actor], Mapping[str, object]]) -> dict:
        if not self._identifier(run_ref) or integer(fence) is None or fence == 0 or not self._identifier(action_id):
            return self._result("rejected", "action_id_invalid")
        with self.entries.scope.environment(PROJECT), self.entries.writing():
            context = self._credential(credential)
            if context is None:
                return self._result("rejected", "credential_unknown")
            _, grant, tenant_id, credential_reason = context
            normalized, intent_hash = self._intent(intent)
            if normalized is None:
                return self._result("rejected", "invalid_action_intent")
            receipt_key = self._action_receipt_key(tenant_id, action_id)
            if prior := self.entries.keyed(receipt_key):
                return self._prior_action(prior[0], intent_hash, tenant_id, action_id)
            action_key = self._action_key(tenant_id, action_id)
            admission = self.entries.keyed(action_key)
            if admission and admission[0].data.get("intent_hash") != intent_hash:
                return self._reused_action(tenant_id, action_id, normalized, intent_hash)
            actor = Actor.system() if credential_reason else self._actor(tenant_id)
            if credential_reason:
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, "rejected", credential_reason, {}, actor)
            if not admission:
                pending_key = self._action_state_key(tenant_id, action_id, "usage-pending")
                if pending := self.entries.keyed(pending_key):
                    if pending[0].data.get("intent_hash") != intent_hash:
                        return self._reused_action(tenant_id, action_id, normalized, intent_hash)
                    if pending[0].data.get("run_ref") == run_ref and pending[0].data.get("fence") == fence:
                        return self._record_result(pending[0], duplicate=True)
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, "rejected", "action_not_admitted", {}, actor)
            if admission[0].data.get("run_ref") != run_ref or admission[0].data.get("fence") != fence:
                return self._result("rejected", "action_admission_mismatch")
            pending_key = self._action_state_key(tenant_id, action_id, "pending")
            self._record("SupervisorActionState", pending_key, tenant_id, {"tenant_id": tenant_id, "action_id": action_id, "run_ref": run_ref, "fence": fence, "intent_hash": intent_hash, "status": "pending", "retry_count": self._retry_count(tenant_id, run_ref)})
            run = self._run(tenant_id, run_ref)
            if reason := self._action_reason(grant, run, fence, normalized, self._now(), apply=True):
                status = "conflicted" if reason in ("stale_fence", "stale_installation_epoch", "lease_expired") else "rejected"
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, status, reason, {}, actor)
            if reason := self._usage_reason(tenant_id, run_ref):
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, "rejected", reason, {}, actor)
            outcome = validate(normalized, grant, run.data)
            if outcome:
                status = outcome.get("status", "rejected")
                reason = outcome.get("reason", "action_precondition_failed")
                if status not in ("conflicted", "rejected") or not isinstance(reason, str):
                    raise ValueError("action validation must return a conflict or rejection")
                return self._save_receipt(tenant_id, action_id, normalized, intent_hash, status, reason, {}, actor)
            result = operation(normalized, actor)
            result_text = canonical(result)
            if result_text is None or not isinstance(result, Mapping):
                raise ValueError("bounded domain operations must return a bounded JSON object")
            receipt = self._save_receipt(tenant_id, action_id, normalized, intent_hash, "applied", "", json.loads(result_text), actor)
            self._finish_applied_run(tenant_id, run_ref, fence)
            return receipt

    def _credential(self, token: str) -> tuple[dict, dict, str, str] | None:
        if not isinstance(token, str) or not token or len(token) > 4096:
            return None
        token_hash = digest(token)
        credentials = self.entries.keyed(self._credential_key(token_hash))
        if not credentials or credentials[0].entry_type != "SupervisorCredential":
            return None
        credential = credentials[0].data
        tenant_id, grant_id = credential.get("tenant_id"), credential.get("grant_id")
        if credential.get("credential_hash") != token_hash or not self._identifier(tenant_id) or not self._identifier(grant_id):
            return None
        grants = self.entries.supervisor_records("SupervisorGrant", last=MAX_DAILY_RUNS, tenant_id=tenant_id, grant_id=grant_id)
        if not grants or len(grants) == MAX_DAILY_RUNS:
            return credential, {}, tenant_id, "grant_unavailable"
        grant = grants[0].data
        reason = ""
        if credential.get("active") is not True:
            reason = "credential_revoked"
        elif self.entries.supervisor_records("SupervisorRevocation", last=1, tenant_id=tenant_id, credential_hash=token_hash):
            reason = "credential_revoked"
        elif integer(grant.get("version")) in (None, 0):
            reason = "grant_version_invalid"
        elif integer(credential.get("grant_version")) != grant.get("version"):
            reason = "credential_grant_stale"
        elif grant.get("status") != "active":
            reason = "grant_inactive"
        elif grant.get("mode") not in ("observe", "apply"):
            reason = "grant_mode_invalid"
        elif not self._unexpired(credential.get("expires_at")) or not self._unexpired(grant.get("expires_at")):
            reason = "grant_expired"
        elif grant.get("tenant_id") != tenant_id:
            reason = "grant_tenant_mismatch"
        elif not self._identifier(grant.get("plan_id")) or not self._identifier(grant.get("node_id")):
            reason = "grant_assignment_invalid"
        elif enrollment_reason := self._enrollment_reason(tenant_id, grant):
            reason = enrollment_reason
        return credential, grant, tenant_id, reason

    def _enrollment_reason(self, tenant_id: str, grant: dict) -> str:
        plan_id, node_id = grant.get("plan_id"), grant.get("node_id")
        enrollments = self.entries.supervisor_records("SupervisorEnrollment", last=MAX_DAILY_RUNS, tenant_id=tenant_id, plan_id=plan_id, node_id=node_id, status="active")
        if not enrollments:
            return "plan_not_enrolled"
        if len(enrollments) == MAX_DAILY_RUNS:
            return "enrollment_set_too_large"
        active = self.entries.supervisor_records("SupervisorGrant", last=MAX_DAILY_RUNS, tenant_id=tenant_id, plan_id=plan_id, node_id=node_id, status="active")
        if len(active) == MAX_DAILY_RUNS:
            return "active_supervisor_set_too_large"
        active_grants = {row.data.get("grant_id") for row in active if self._identifier(row.data.get("grant_id"))}
        if len(active_grants) != 1:
            return "active_supervisor_not_unique"
        if grant.get("grant_id") not in active_grants:
            return "supervisor_assignment_mismatch"
        return ""

    def _unexpired(self, value: object) -> bool:
        expires = parsed_time(value)
        return expires is not None and expires > self._now()

    def _observation_reason(self, grant: dict, observation: Mapping[str, object], now: datetime) -> str:
        episode_id, fingerprint = observation.get("episode_id"), observation.get("problem_fingerprint")
        observed = parsed_time(observation.get("observed_at"))
        generation, count = integer(observation.get("evidence_generation")), integer(observation.get("work_count"))
        if not self._identifier(episode_id) or not self._identifier(fingerprint) or generation is None or observed is None:
            return "invalid_observation"
        if observed > now or (now - observed).total_seconds() > MAX_OBSERVATION_AGE:
            return "stale_observation"
        if count == 0:
            return "empty_work"
        if count is None or observation.get("eligible") is not True:
            return "ineligible_work"
        phase_revision, grant_revision = integer(observation.get("phase_revision")), integer(grant.get("phase_revision"))
        if phase_revision is None or grant_revision is None or phase_revision != grant_revision:
            return "stale_phase_revision"
        gates = observation.get("gates")
        if not isinstance(gates, Mapping) or not gates or any(value is not True for value in gates.values()):
            return "ineligible_gate"
        return ""

    def _rates(self, model: object) -> tuple[Decimal, Decimal] | None:
        if not isinstance(model, str) or model not in self.prices:
            return None
        pair = self.prices[model]
        if not isinstance(pair, tuple) or len(pair) != 2:
            return None
        input_rate, output_rate = positive_decimal(pair[0]), positive_decimal(pair[1])
        return (input_rate, output_rate) if input_rate is not None and output_rate is not None else None

    def _reservation(self, grant: dict, rates: tuple[Decimal, Decimal]) -> dict | None:
        budget = grant.get("budget")
        if not isinstance(budget, Mapping):
            return None
        retries = integer(budget.get("max_retries"))
        input_per_turn = integer(budget.get("input_tokens_per_turn"))
        output_per_turn = integer(budget.get("output_tokens_per_turn"))
        if retries is None or retries > MAX_RETRIES or not input_per_turn or not output_per_turn:
            return None
        turns = retries + 1
        input_tokens, output_tokens = input_per_turn * turns, output_per_turn * turns
        input_rate, output_rate = rates
        return {
            "cost_usd": str(cost(input_tokens, output_tokens, input_rate, output_rate)),
            "turns": turns,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_rate_per_million": str(input_rate),
            "output_rate_per_million": str(output_rate),
            "max_retries": retries,
        }

    def _budget_available(self, tenant_id: str, grant: dict, reservation: dict, day: str) -> bool:
        budget = grant.get("budget")
        if not isinstance(budget, Mapping):
            return False
        daily_cost = positive_decimal(budget.get("daily_cost_usd"))
        daily_turns = integer(budget.get("daily_turns"))
        daily_input = integer(budget.get("daily_input_tokens"))
        daily_output = integer(budget.get("daily_output_tokens"))
        if daily_cost is None or daily_turns is None or daily_turns > MAX_DAILY_RUNS or not daily_input or not daily_output:
            return False
        runs = self.entries.supervisor_records("SupervisorRun", last=MAX_DAILY_RUNS, tenant_id=tenant_id, day=day)
        if len(runs) >= MAX_DAILY_RUNS:
            return False
        used_cost, used_turns, used_input, used_output = Decimal(0), 0, 0, 0
        for run in runs:
            reserved = run.data.get("reservation")
            run_ref = run.data.get("run_ref")
            if not isinstance(reserved, Mapping) or not isinstance(run_ref, str):
                return False
            usage_rows = self.entries.keyed(self._usage_key(tenant_id, run_ref))
            if usage_rows:
                usage = usage_rows[0].data
                if usage.get("overrun") is True:
                    return False
                actual_cost = decimal_amount(usage.get("cost_usd"))
                actual_turns = integer(usage.get("turns"))
                actual_input = integer(usage.get("input_tokens"))
                actual_output = integer(usage.get("output_tokens"))
                if actual_cost is None or actual_turns is None or actual_input is None or actual_output is None:
                    return False
                used_cost += actual_cost
                used_turns += actual_turns
                used_input += actual_input
                used_output += actual_output
            else:
                used_cost += Decimal(reserved["cost_usd"])
                used_turns += reserved["turns"]
                used_input += reserved["input_tokens"]
                used_output += reserved["output_tokens"]
        return used_cost + Decimal(reservation["cost_usd"]) <= daily_cost and used_turns + reservation["turns"] <= daily_turns and used_input + reservation["input_tokens"] <= daily_input and used_output + reservation["output_tokens"] <= daily_output

    def _active_run(self, tenant_id: str, plan_id: str, node_id: str, installation_epoch: int, now: datetime) -> bool:
        run = self._latest_run(tenant_id, plan_id, node_id)
        if run is None or run.data.get("installation_epoch") != installation_epoch:
            return False
        state = self._latest_run_state(tenant_id, run.data["run_ref"])
        status = state.data["status"] if state else run.data["status"]
        lease_until = parsed_time(run.data["lease_until"])
        return status not in TERMINAL_RUN_STATES and lease_until is not None and lease_until > now

    def _latest_run(self, tenant_id: str, plan_id: str, node_id: str) -> Entry | None:
        rows = self.entries.supervisor_records("SupervisorRun", last=1, tenant_id=tenant_id, plan_id=plan_id, node_id=node_id)
        return rows[0] if rows else None

    def _run(self, tenant_id: str, run_ref: str) -> Entry | None:
        rows = self.entries.supervisor_records("SupervisorRun", last=1, tenant_id=tenant_id, run_ref=run_ref)
        return rows[0] if rows else None

    def _installation(self, tenant_id: str) -> dict | None:
        rows = self.entries.supervisor_records("SupervisorInstallation", last=1, tenant_id=tenant_id)
        return rows[0].data if rows else None

    def _latest_run_state(self, tenant_id: str, run_ref: str) -> Entry | None:
        rows = self.entries.supervisor_records("SupervisorRunState", last=1, tenant_id=tenant_id, run_ref=run_ref)
        return rows[0] if rows else None

    def _run_reason(self, grant: dict, run: Entry | None, fence: int, now: datetime) -> str:
        if run is None:
            return "run_unknown"
        tenant_id = run.data.get("tenant_id", "")
        if run.data.get("grant_id") != grant.get("grant_id") or run.data.get("grant_version") != grant.get("version"):
            return "grant_stale"
        installation = self._installation(tenant_id)
        if installation is None or installation.get("epoch") != run.data.get("installation_epoch"):
            return "stale_installation_epoch"
        latest = self._latest_run(tenant_id, run.data.get("plan_id", ""), run.data.get("node_id", ""))
        if latest is None or latest.data.get("run_ref") != run.data.get("run_ref") or latest.data.get("fence") != fence:
            return "stale_fence"
        if run.data.get("fence") != fence:
            return "stale_fence"
        if (lease_until := parsed_time(run.data.get("lease_until"))) is None or lease_until <= now:
            return "lease_expired"
        state = self._latest_run_state(tenant_id, run.data["run_ref"])
        if state and state.data.get("status") in TERMINAL_RUN_STATES:
            return "run_complete"
        return ""

    def _action_reason(self, grant: dict, run: Entry | None, fence: int, intent: dict, now: datetime, apply: bool = False) -> str:
        if reason := self._run_reason(grant, run, fence, now):
            return reason
        if apply and grant.get("mode") != "apply":
            return "grant_mode_observe_only"
        if integer(intent.get("grant_version")) is None or intent.get("grant_version") != grant.get("version"):
            return "grant_version_stale"
        if intent.get("episode_id") != run.data.get("episode_id"):
            return "episode_mismatch"
        kind = intent.get("kind")
        allowed_actions = grant.get("allowed_actions")
        if not isinstance(kind, str) or not isinstance(allowed_actions, (list, tuple)) or kind not in allowed_actions:
            return "action_not_granted"
        revisions = intent.get("expected_revisions")
        if not isinstance(revisions, Mapping) or not revisions or any(not self._identifier(key) or integer(value) is None for key, value in revisions.items()):
            return "expected_revisions_missing"
        return ""

    def _usage_reason(self, tenant_id: str, run_ref: str) -> str:
        rows = self.entries.keyed(self._usage_key(tenant_id, run_ref))
        if not rows:
            return "usage_unknown"
        return "usage_overrun" if rows[0].data.get("overrun") is True else ""

    def _intent(self, intent: Mapping[str, object]) -> tuple[dict | None, str]:
        if not isinstance(intent, Mapping) or any(not isinstance(key, str) for key in intent):
            return None, ""
        text = canonical(dict(intent))
        return (json.loads(text), digest(text)) if text is not None else (None, "")

    def _record(self, entry_type: str, key: str, tenant_id: str, data: dict, actor: Actor | None = None) -> Entry:
        actor = actor or self._actor(tenant_id)
        return self.control_entries.recorded(Entry(environment_id=PROJECT, entry_type=entry_type, actor=actor, data=data, idempotency=key), actor)

    def _actor(self, tenant_id: str) -> Actor:
        return Actor.external(f"supervisor:{tenant_id}")

    def _record_result(self, row: Entry, duplicate: bool = False) -> dict:
        return {"status": row.data.get("status", "admitted"), "receipt_id": row.id, "run_ref": row.data.get("run_ref"), "fence": row.data.get("fence"), "epoch": row.data.get("epoch", row.data.get("installation_epoch")), "data": row.data, "duplicate": duplicate}

    def _result(self, status: str, reason: str, **values) -> dict:
        return {"status": status, "reason": reason, **values}

    def _save_receipt(self, tenant_id: str, action_id: str, intent: dict, intent_hash: str, status: str, reason: str, result: dict, actor: Actor) -> dict:
        key = self._action_receipt_key(tenant_id, action_id)
        if prior := self.entries.keyed(key):
            return self._prior_action(prior[0], intent_hash, tenant_id, action_id)
        admission = self.entries.keyed(self._action_key(tenant_id, action_id))
        admission_data = admission[0].data if admission else {}
        run_ref, fence = admission_data.get("run_ref"), admission_data.get("fence")
        state = {"tenant_id": tenant_id, "action_id": action_id, "run_ref": run_ref, "fence": fence, "intent_hash": intent_hash, "status": status, "reason": reason, "retry_count": self._retry_count(tenant_id, run_ref) if isinstance(run_ref, str) else 0}
        self._record("SupervisorActionState", self._action_state_key(tenant_id, action_id, status), tenant_id, state, actor)
        row = self._record("SupervisorActionReceipt", key, tenant_id, {"tenant_id": tenant_id, "action_id": action_id, "intent": intent, "intent_hash": intent_hash, "status": status, "reason": reason, "result": result}, actor)
        return self._record_result(row)

    def _prior_action(self, prior: Entry, intent_hash: str, tenant_id: str, action_id: str) -> dict:
        return self._record_result(prior, duplicate=True) if prior.data.get("intent_hash") == intent_hash else self._reused_action(tenant_id, action_id, prior.data.get("intent", {}), intent_hash)

    def _reused_action(self, tenant_id: str, action_id: str, intent: dict, intent_hash: str) -> dict:
        key = self._key("action-reuse", tenant_id, action_id, intent_hash)
        if prior := self.entries.keyed(key):
            return self._record_result(prior[0], duplicate=True)
        row = self._record("SupervisorActionReceipt", key, tenant_id, {"tenant_id": tenant_id, "action_id": action_id, "intent": intent, "intent_hash": intent_hash, "status": "rejected", "reason": "action_id_reused", "result": {}}, self._actor(tenant_id))
        return self._record_result(row)

    def _finish_applied_run(self, tenant_id: str, run_ref: str, fence: int) -> None:
        key = self._run_state_key(tenant_id, run_ref, "complete")
        latest = self._latest_run_state(tenant_id, run_ref)
        retries = latest.data["retry_count"] if latest else 0
        self._record("SupervisorRunState", key, tenant_id, {"tenant_id": tenant_id, "run_ref": run_ref, "fence": fence, "status": "complete", "retry_count": retries})

    def _retry_count(self, tenant_id: str, run_ref: str) -> int:
        latest = self._latest_run_state(tenant_id, run_ref)
        return latest.data["retry_count"] if latest else 0

    def _now(self) -> datetime:
        value = parsed_time(self.clock())
        if value is None:
            raise ValueError("supervisor admission needs an aware clock")
        return value

    def _identifier(self, value: object) -> bool:
        if not isinstance(value, str) or not value:
            return False
        try:
            return len(value.encode("utf-8")) <= MAX_IDENTIFIER_BYTES
        except UnicodeEncodeError:
            return False

    def _key(self, kind: str, *parts: str) -> str:
        return supervisor_key(kind, *parts)

    def _credential_key(self, token_hash: str) -> str:
        return f"supervisor:credential:{token_hash}"

    def _usage_key(self, tenant_id: str, run_ref: str) -> str:
        return self._key("usage", tenant_id, run_ref)

    def _usage_pending_key(self, tenant_id: str, run_ref: str) -> str:
        return self._key("usage-pending", tenant_id, run_ref)

    def _run_state_key(self, tenant_id: str, run_ref: str, state: str) -> str:
        return self._key("run-state", tenant_id, run_ref, state)

    def _action_key(self, tenant_id: str, action_id: str) -> str:
        return self._key("action", tenant_id, action_id)

    def _action_receipt_key(self, tenant_id: str, action_id: str) -> str:
        return action_receipt_key(tenant_id, action_id)

    def _action_state_key(self, tenant_id: str, action_id: str, state: str) -> str:
        return self._key("action-state", tenant_id, action_id, state)

