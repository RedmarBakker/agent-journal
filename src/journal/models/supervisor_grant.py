from dataclasses import dataclass, replace
from typing import Mapping

from journal.models.supervisor_narrowing_rule import SupervisorNarrowingRule

BUDGET_FIELDS = frozenset({
    "max_turns_per_day", "max_input_tokens_per_turn", "max_output_tokens_per_turn",
    "max_provider_requests_per_turn", "max_turn_seconds", "max_cost_microusd_per_day",
    "max_bundles_per_project_day", "max_bundles_per_episode_day", "max_new_diagnostics_per_episode",
})
MAX_INPUT_TOKENS_PER_TURN = 80_000
EVENT_WAKEUPS = frozenset({"failed_check", "stalled_task", "stale_worker", "message_to_supervisor", "question_to_supervisor"})
VERSION_ONE_CAPABILITIES = {
    "diagnostic_task": "task create",
    "plan_priorities": "plan priorities",
    "check_interval": "check edit",
}


@dataclass(frozen=True)
class SupervisorGrant:
    """One environment's supervisor permissions, scope, wake settings and limits."""

    owner_user_id: int
    environment_id: int
    watched_plans: str | tuple[int, ...]
    capabilities: tuple[tuple[str, bool, str], ...]
    wake_interval_minutes: int
    event_wakeups: tuple[str, ...]
    limits: tuple[tuple[str, int], ...]
    valid_until_ms: int
    paused: bool
    revoked: bool
    rules: tuple[SupervisorNarrowingRule, ...] = ()

    @classmethod
    def parsed(cls, value: object, catalogue: Mapping[str, tuple[str, int | str]]) -> "SupervisorGrant":
        data = cls._fields(value)
        return cls._converted(data, cls._capabilities(data["capabilities"], catalogue), cls._rules(data["rules"], catalogue))

    @classmethod
    def stored(cls, value: object) -> "SupervisorGrant":
        data = cls._fields(value)
        return cls._converted(data, cls._stored_capabilities(data["capabilities"]), cls._stored_rules(data["rules"]))

    @classmethod
    def _fields(cls, value: object) -> dict:
        fields = {
            "owner_user_id", "environment_id", "watched_plans", "capabilities", "wake_interval_minutes",
            "event_wakeups", "limits", "valid_until_ms", "paused", "revoked", "rules",
        }
        if isinstance(value, dict) and set(value) == fields - {"rules"}:
            return {**value, "rules": []}
        return cls._object(value, fields)

    @classmethod
    def _converted(cls, data: dict, capabilities: tuple[tuple[str, bool, str], ...],
                   rules: tuple[SupervisorNarrowingRule, ...]) -> "SupervisorGrant":
        owner = cls._integer(data["owner_user_id"], 1)
        environment = cls._integer(data["environment_id"], 1)
        plans = cls._plans(data["watched_plans"])
        interval = data["wake_interval_minutes"]
        if type(interval) is not int or interval not in (15, 30, 60):
            raise ValueError("the supervisor grant wake interval must be 15, 30 or 60 minutes")
        events = cls._events(data["event_wakeups"])
        limits = cls._limits(data["limits"])
        valid_until = cls._integer(data["valid_until_ms"], 1)
        if type(data["paused"]) is not bool:
            raise ValueError("the supervisor grant paused field must be on or off")
        if type(data["revoked"]) is not bool:
            raise ValueError("the supervisor grant revoked field must be on or off")
        return cls(owner, environment, plans, capabilities, interval, events, limits, valid_until,
                   data["paused"], data["revoked"], rules)

    @classmethod
    def from_version_one(cls, grant: dict) -> "SupervisorGrant":
        mode = "propose" if grant["mode"] == "shadow" else "act"
        capabilities = tuple(sorted(
            (command, cls._boolean(grant["capabilities"][legacy]), mode)
            for legacy, command in VERSION_ONE_CAPABILITIES.items()
        ))
        return cls(
            cls._integer(grant["owner_user_id"], 1), cls._integer(grant["driver_environment_id"], 1),
            cls._plans([grant["plan_id"]]), capabilities, 15, cls._events(["failed_check"]),
            cls._limits(grant["limits"]), cls._integer(grant["valid_until_ms"], 1), False, cls._boolean(grant["revoked"]),
        )

    def data(self) -> dict:
        return {
            "owner_user_id": self.owner_user_id,
            "environment_id": self.environment_id,
            "watched_plans": self.watched_plans if self.watched_plans == "all" else list(self.watched_plans),
            "capabilities": {name: {"on": enabled, "mode": mode} for name, enabled, mode in self.capabilities},
            "wake_interval_minutes": self.wake_interval_minutes,
            "event_wakeups": list(self.event_wakeups),
            "limits": dict(self.limits),
            "valid_until_ms": self.valid_until_ms,
            "paused": self.paused,
            "revoked": self.revoked,
            "rules": [rule.data() for rule in self.rules],
        }

    def with_revoked(self) -> "SupervisorGrant":
        return SupervisorGrant(self.owner_user_id, self.environment_id, self.watched_plans, self.capabilities,
                               self.wake_interval_minutes, self.event_wakeups, self.limits, self.valid_until_ms,
                               self.paused, True, self.rules)

    def tier_three_decision(self, command: str, catalogue: Mapping[str, tuple[str, int | str]]) -> str:
        entry = catalogue.get(command)
        if entry is None:
            raise ValueError("the supervisor command is not in the catalogue")
        _area, tier = entry
        if tier == "never":
            raise ValueError("a command marked Never cannot have an owner decision")
        if tier not in (3, "tier 3"):
            raise ValueError("only tier 3 commands can have an owner decision")
        setting = next(((enabled, mode) for name, enabled, mode in self.capabilities if name == command), None)
        if setting is None:
            return "propose_only"
        enabled, mode = setting
        return "not_allowed" if not enabled else "may_act" if mode == "act" else "propose_only"

    def with_tier_three_decision(self, command: str, decision: str,
                                 catalogue: Mapping[str, tuple[str, int | str]]) -> "SupervisorGrant":
        if decision not in ("not_allowed", "propose_only", "may_act"):
            raise ValueError("the supervisor decision must be Not allowed, Propose only or May act")
        current = self.tier_three_decision(command, catalogue)
        if current == decision:
            return self
        capabilities = {name: (enabled, mode) for name, enabled, mode in self.capabilities}
        capabilities[command] = (decision != "not_allowed", "act" if decision == "may_act" else "propose")
        return SupervisorGrant(
            self.owner_user_id, self.environment_id, self.watched_plans,
            tuple((name, enabled, mode) for name, (enabled, mode) in sorted(capabilities.items())),
            self.wake_interval_minutes, self.event_wakeups, self.limits, self.valid_until_ms,
            self.paused, self.revoked, self.rules,
        )

    def rule_for(self, command: str, row_id: int | None) -> SupervisorNarrowingRule | None:
        denied = next((rule for rule in self.rules if rule.command == command
                       and rule.effect == "never" and (row_id is None or rule.row_id == row_id)), None)
        return denied or next(
            (rule for rule in self.rules if rule.command == command and rule.effect == "propose"), None,
        )

    def with_rule(self, rule: SupervisorNarrowingRule) -> "SupervisorGrant":
        if rule in self.rules:
            raise ValueError("the supervisor narrowing rule is already saved")
        rules = tuple(sorted((*self.rules, rule), key=lambda item: (item.command, item.effect, item.row_id or 0)))
        return SupervisorGrant(self.owner_user_id, self.environment_id, self.watched_plans, self.capabilities,
                               self.wake_interval_minutes, self.event_wakeups, self.limits, self.valid_until_ms,
                               self.paused, self.revoked, rules)

    def without_rule(self, rule: SupervisorNarrowingRule) -> "SupervisorGrant":
        if rule not in self.rules:
            raise ValueError("the supervisor narrowing rule is not saved")
        rules = tuple(saved for saved in self.rules if saved != rule)
        return SupervisorGrant(self.owner_user_id, self.environment_id, self.watched_plans, self.capabilities,
                               self.wake_interval_minutes, self.event_wakeups, self.limits, self.valid_until_ms,
                               self.paused, self.revoked, rules)

    @classmethod
    def _rules(cls, value: object, catalogue: Mapping[str, tuple[str, int | str]]) -> tuple[SupervisorNarrowingRule, ...]:
        if not isinstance(value, list):
            raise ValueError("the supervisor narrowing rules must be a list")
        commands = set(catalogue)
        rules = tuple(SupervisorNarrowingRule.parsed(rule, commands) for rule in value)
        if len(rules) != len(set(rules)):
            raise ValueError("the supervisor narrowing rules must be unique")
        return rules

    @classmethod
    def _stored_rules(cls, value: object) -> tuple[SupervisorNarrowingRule, ...]:
        if not isinstance(value, list):
            raise ValueError("the supervisor narrowing rules must be a list")
        rules = tuple(SupervisorNarrowingRule.stored(rule) for rule in value)
        if len(rules) != len(set(rules)):
            raise ValueError("the supervisor narrowing rules must be unique")
        return rules

    def with_wake_interval(self, minutes: int) -> "SupervisorGrant":
        if type(minutes) is not int or minutes not in (15, 30, 60):
            raise ValueError("the supervisor grant wake interval must be 15, 30 or 60 minutes")
        return replace(self, wake_interval_minutes=minutes)

    @classmethod
    def _capabilities(cls, value: object, catalogue: Mapping[str, tuple[str, int | str]]) -> tuple[tuple[str, bool, str], ...]:
        result = []
        for selector, enabled, mode in cls._capability_settings(value):
            matches = cls._matches(selector, catalogue)
            if not matches:
                if isinstance(selector, str) and selector.startswith("area:"):
                    raise ValueError("the supervisor grant area is not in the catalogue")
                raise ValueError("the supervisor grant capability is not in the catalogue")
            if enabled:
                all_tiers = [cls._tier_number(tier) for _area, tier in matches]
                tiers = [tier for tier in all_tiers if tier != "read"]
                if "never" in tiers:
                    raise ValueError("the supervisor grant capability mode exceeds its safety tier")
                if any(tier not in (1, 2, 3) for tier in tiers):
                    raise ValueError("the supervisor grant capability has an unknown safety tier")
            result.append((selector, enabled, mode))
        return tuple(sorted(result))

    @classmethod
    def _stored_capabilities(cls, value: object) -> tuple[tuple[str, bool, str], ...]:
        return tuple(sorted(cls._capability_settings(value)))

    @classmethod
    def _capability_settings(cls, value: object) -> list[tuple[str, bool, str]]:
        if not isinstance(value, dict):
            raise ValueError("the supervisor grant capabilities must be an object")
        result = []
        for selector, raw in value.items():
            setting = cls._object(raw, {"on", "mode"})
            if (not isinstance(selector, str) or not selector or type(setting["on"]) is not bool
                    or setting["mode"] not in ("propose", "act")):
                raise ValueError("the supervisor grant capability must choose On or Off and Propose or Act")
            result.append((selector, setting["on"], setting["mode"]))
        return result

    @staticmethod
    def _matches(selector: object, catalogue: Mapping[str, tuple[str, int | str]]) -> list[tuple[str, int | str]]:
        if not isinstance(selector, str) or not selector:
            return []
        if selector.startswith("area:"):
            area = selector.removeprefix("area:")
            return [entry for entry in catalogue.values() if entry[0] == area]
        entry = catalogue.get(selector)
        return [entry] if entry is not None else []

    @staticmethod
    def _tier_number(tier: int | str) -> int | str:
        return {"tier 1": 1, "tier 2": 2, "tier 3": 3}.get(tier, tier)

    @staticmethod
    def _plans(value: object) -> str | tuple[int, ...]:
        if value == "all":
            return "all"
        if (not isinstance(value, list) or any(type(plan) is not int or plan < 1 for plan in value)
                or len(value) != len(set(value))):
            raise ValueError("the supervisor grant watched plans must be all or a unique list of plan ids")
        return tuple(value)

    @classmethod
    def _limits(cls, value: object) -> tuple[tuple[str, int], ...]:
        if not isinstance(value, dict) or set(value) != BUDGET_FIELDS:
            raise ValueError("the supervisor grant limits must contain one daily cost limit")
        limits = value
        for name, amount in limits.items():
            maximum = MAX_INPUT_TOKENS_PER_TURN if name == "max_input_tokens_per_turn" else None
            if type(amount) is not int or amount < 1 or maximum is not None and amount > maximum:
                raise ValueError("the supervisor grant limits must be positive integers within their bounds")
        if limits["max_new_diagnostics_per_episode"] != 1:
            raise ValueError("the supervisor grant allows one new diagnostic per episode")
        return tuple(sorted(limits.items()))

    @staticmethod
    def _events(value: object) -> tuple[str, ...]:
        if (not isinstance(value, list) or any(not isinstance(event, str) or event not in EVENT_WAKEUPS for event in value)
                or len(value) != len(set(value))):
            raise ValueError("the supervisor grant event wakeups are invalid")
        return tuple(sorted(value))

    @staticmethod
    def _object(value: object, fields: set[str] | frozenset[str]) -> dict:
        if not isinstance(value, dict) or set(value) != set(fields):
            raise ValueError("the supervisor grant fields are invalid")
        return value

    @staticmethod
    def _integer(value: object, minimum: int) -> int:
        if type(value) is not int or value < minimum:
            raise ValueError("the supervisor grant integer field is invalid")
        return value

    @staticmethod
    def _boolean(value: object) -> bool:
        if type(value) is not bool:
            raise ValueError("the supervisor grant boolean field is invalid")
        return value
