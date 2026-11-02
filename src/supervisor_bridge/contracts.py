import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


PINNED_OPENCLAW_VERSION = "2026.10.8"
PINNED_OPENCLAW_COMMIT = "dc2523e5a5c7a309517fd7fa834add938231d526"
CONTRACT_VERSION = 1
CONTRACT_SCHEMA_SHA256 = "6b4b0e7cdce82633a2fafcae918b87bd1001226d26e45348cfe3fbe0802bc211"
TOOL_NAMES = (
    "journal_supervisor.observe",
    "journal_supervisor.apply_maintenance",
    "journal_supervisor.receipt",
)
OPENCLAW_TOOL_NAMES = (
    "journal__journal_supervisor-observe",
    "journal__journal_supervisor-apply_maintenance",
    "journal__journal_supervisor-receipt",
)
METERED_PROVIDER_BASE_URL = "http://127.0.0.1:17840"
RUN_KEYS = frozenset({
    "run_id",
    "episode_id",
    "pending_action_id",
    "grant_id",
    "grant_version",
    "installation_epoch",
    "fence",
    "lease_expires_at_ms",
    "budget_reservation_id",
    "reserved_cost_microusd",
})
RUN_REFERENCE_KEYS = frozenset({
    "run_id",
    "episode_id",
    "pending_action_id",
    "grant_id",
    "grant_version",
    "installation_epoch",
    "fence",
})
ROUTES = {
    "admit": "/_supervisor/v1/admit",
    "observe": "/_supervisor/v1/observe",
    "usage": "/_supervisor/v1/usage",
    "apply": "/_supervisor/v1/apply",
    "receipt": "/_supervisor/v1/receipt",
}
FIXTURE_PATH = Path(__file__).resolve().parents[2] / "docs" / "supervisor" / "v1" / "fixtures.json"
SCHEMA_PATH = FIXTURE_PATH.with_name("contract.schema.json")


class ContractError(ValueError):
    """A request or response does not match the closed supervisor contract."""


@dataclass(frozen=True)
class RunReference:
    """The bounded server-issued run identity and fence used by every tool."""

    run_id: str
    episode_id: str
    pending_action_id: str
    grant_id: str
    grant_version: int
    installation_epoch: int
    fence: int

    @classmethod
    def from_run(cls, value: object) -> "RunReference":
        run = strict_object(value, RUN_KEYS, RUN_KEYS, "run")
        for key in ("run_id", "episode_id", "pending_action_id", "grant_id", "budget_reservation_id"):
            bounded_text(run[key], key, 1, 256)
        for key in ("grant_version", "installation_epoch", "fence", "reserved_cost_microusd"):
            positive_integer(run[key], key)
        nonnegative_integer(run["lease_expires_at_ms"], "lease_expires_at_ms")
        return cls(
            run["run_id"],
            run["episode_id"],
            run["pending_action_id"],
            run["grant_id"],
            run["grant_version"],
            run["installation_epoch"],
            run["fence"],
        )

    @classmethod
    def from_reference(cls, value: object) -> "RunReference":
        reference = strict_object(value, RUN_REFERENCE_KEYS, RUN_REFERENCE_KEYS, "run_ref")
        for key in ("run_id", "episode_id", "pending_action_id", "grant_id"):
            bounded_text(reference[key], key, 1, 256)
        for key in ("grant_version", "installation_epoch", "fence"):
            positive_integer(reference[key], key)
        return cls(
            reference["run_id"],
            reference["episode_id"],
            reference["pending_action_id"],
            reference["grant_id"],
            reference["grant_version"],
            reference["installation_epoch"],
            reference["fence"],
        )

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "pending_action_id": self.pending_action_id,
            "grant_id": self.grant_id,
            "grant_version": self.grant_version,
            "installation_epoch": self.installation_epoch,
            "fence": self.fence,
        }


def strict_object(value: object, required: frozenset[str], allowed: frozenset[str], name: str) -> dict:
    if not isinstance(value, dict):
        raise ContractError(f"{name} must be an object")
    if set(value) != allowed or not required.issubset(value):
        raise ContractError(f"{name} has missing or unsupported fields")
    return value


def bounded_text(value: object, name: str, minimum: int, maximum: int) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ContractError(f"{name} must be a bounded string")
    return value


def positive_integer(value: object, name: str) -> int:
    if type(value) is not int or value < 1:
        raise ContractError(f"{name} must be a positive integer")
    return value


def nonnegative_integer(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ContractError(f"{name} must be a nonnegative integer")
    return value


def bounded_cursor(value: object) -> str | None:
    if value is None:
        return None
    return bounded_text(value, "cursor", 1, 256)


def action_request(reference: RunReference, arguments: object) -> dict:
    fields = frozenset({"run_ref", "observation_ids", "expected_revisions", "operations", "rationale"})
    values = strict_object(arguments, fields, fields, "apply_maintenance arguments")
    supplied_reference = RunReference.from_reference(values["run_ref"])
    if supplied_reference != reference:
        raise ContractError("run_ref does not match the admitted fenced run")
    observations = values["observation_ids"]
    revisions = values["expected_revisions"]
    operations = values["operations"]
    rationale = bounded_text(values["rationale"], "rationale", 1, 2048)
    if not isinstance(observations, list) or not 1 <= len(observations) <= 20:
        raise ContractError("observation_ids must contain 1 to 20 references")
    for observation in observations:
        bounded_text(observation, "observation_id", 1, 256)
    if not isinstance(revisions, list) or not 2 <= len(revisions) <= 12:
        raise ContractError("expected_revisions must contain 2 to 12 references")
    for revision in revisions:
        values_for_revision = strict_object(
            revision,
            frozenset({"ref", "revision"}),
            frozenset({"ref", "revision"}),
            "expected revision",
        )
        row_ref = strict_object(
            values_for_revision["ref"],
            frozenset({"table", "id"}),
            frozenset({"table", "id"}),
            "row reference",
        )
        if not isinstance(row_ref["table"], str) or row_ref["table"] not in {"plans", "phases", "tasks", "checks"}:
            raise ContractError("row reference table is not managed by this contract")
        positive_integer(row_ref["id"], "row reference id")
        bounded_text(values_for_revision["revision"], "revision", 1, 256)
    if not isinstance(operations, list) or not 1 <= len(operations) <= 5:
        raise ContractError("operations must contain 1 to 5 typed changes")
    for operation in operations:
        validate_operation(operation)
    return {
        "protocol_version": CONTRACT_VERSION,
        "run_id": reference.run_id,
        "installation_epoch": reference.installation_epoch,
        "fence": reference.fence,
        "grant_version": reference.grant_version,
        "episode_id": reference.episode_id,
        "action_id": reference.pending_action_id,
        "observation_ids": observations,
        "expected_revisions": revisions,
        "operations": operations,
        "rationale": rationale,
    }


def validate_operation(value: object) -> None:
    if not isinstance(value, dict) or not isinstance(value.get("kind"), str):
        raise ContractError("operation must be a typed object")
    kind = value["kind"]
    schemas = {
        "plan_priorities": frozenset({"kind", "plan_id", "text"}),
        "diagnostic_task": frozenset({"kind", "plan_id", "phase_id", "template_id", "template_revision", "evidence_ids"}),
        "check_interval": frozenset({"kind", "check_id", "interval_minutes"}),
    }
    fields = schemas.get(kind)
    if fields is None:
        raise ContractError("operation kind is not enabled")
    strict_object(value, fields, fields, "operation")
    if kind == "plan_priorities":
        positive_integer(value["plan_id"], "plan_id")
        bounded_text(value["text"], "priorities text", 1, 2048)
    elif kind == "diagnostic_task":
        positive_integer(value["plan_id"], "plan_id")
        positive_integer(value["phase_id"], "phase_id")
        bounded_text(value["template_id"], "template_id", 1, 256)
        bounded_text(value["template_revision"], "template_revision", 1, 256)
        evidence_ids = value["evidence_ids"]
        if not isinstance(evidence_ids, list) or not 1 <= len(evidence_ids) <= 20:
            raise ContractError("evidence_ids must contain 1 to 20 references")
        for evidence_id in evidence_ids:
            bounded_text(evidence_id, "evidence_id", 1, 256)
    else:
        positive_integer(value["check_id"], "check_id")
        interval = value["interval_minutes"]
        if type(interval) is not int or not 5 <= interval <= 30:
            raise ContractError("interval_minutes must be between 5 and 30")


def load_contract_schema() -> dict:
    contents = SCHEMA_PATH.read_bytes()
    if hashlib.sha256(contents).hexdigest() != CONTRACT_SCHEMA_SHA256:
        raise ContractError("supervisor contract schema differs from the pinned version")
    schema = json.loads(contents)
    if schema.get("$id") != "urn:journal:proactive-supervisor:contract:1":
        raise ContractError("supervisor contract schema id differs from the pin")
    return schema


def inline_schema(value: object, definitions: dict) -> object:
    if isinstance(value, list):
        return [inline_schema(item, definitions) for item in value]
    if not isinstance(value, dict):
        return value
    reference = value.get("$ref")
    if isinstance(reference, str) and reference.startswith("#/$defs/"):
        return inline_schema(copy.deepcopy(definitions[reference.rsplit("/", 1)[1]]), definitions)
    return {key: inline_schema(item, definitions) for key, item in value.items()}


def tool_input_schemas(schema: dict | None = None) -> dict[str, dict]:
    contract = schema or load_contract_schema()
    definitions = contract["$defs"]
    request_properties = definitions["ObserveRequest"]["properties"]
    action_properties = definitions["ActionRequest"]["properties"]
    run_properties = definitions["Run"]["properties"]
    run_ref = {
        "type": "object",
        "properties": {
            key: copy.deepcopy(run_properties[key])
            for key in sorted(RUN_REFERENCE_KEYS)
        },
        "required": sorted(RUN_REFERENCE_KEYS),
        "additionalProperties": False,
    }
    return {
        TOOL_NAMES[0]: {
            "type": "object",
            "properties": {
                "run_ref": run_ref,
                "cursor": inline_schema(request_properties["cursor"], definitions),
            },
            "required": ["run_ref", "cursor"],
            "additionalProperties": False,
        },
        TOOL_NAMES[1]: {
            "type": "object",
            "properties": {
                "run_ref": run_ref,
                "observation_ids": inline_schema(action_properties["observation_ids"], definitions),
                "expected_revisions": inline_schema(action_properties["expected_revisions"], definitions),
                "operations": inline_schema(action_properties["operations"], definitions),
                "rationale": inline_schema(action_properties["rationale"], definitions),
            },
            "required": [
                "run_ref",
                "observation_ids",
                "expected_revisions",
                "operations",
                "rationale",
            ],
            "additionalProperties": False,
        },
        TOOL_NAMES[2]: {
            "type": "object",
            "properties": {"run_ref": run_ref},
            "required": ["run_ref"],
            "additionalProperties": False,
        },
    }


def effective_tool_inventory(config: dict, discovered: set[str]) -> list[str]:
    allowed = config["openclaw_config"]["agents"]["entries"]["supervisor"]["tools"]["allow"]
    return [name for name in allowed if name in discovered]


def validate_pinned_fixture(fixture: dict) -> None:
    if fixture.get("contract_version") != CONTRACT_VERSION:
        raise ContractError("fixture uses an unsupported supervisor contract version")
    if fixture.get("openclaw_pin") != {
        "version": PINNED_OPENCLAW_VERSION,
        "commit": PINNED_OPENCLAW_COMMIT,
    }:
        raise ContractError("fixture is not pinned to the reviewed OpenClaw release")
    expected_tool_names = list(OPENCLAW_TOOL_NAMES)
    expected_config = {
        "auth": {
            "profiles": {"anthropic:supervisor-api": {"provider": "anthropic", "mode": "api_key"}},
            "order": {"anthropic": ["anthropic:supervisor-api"]},
        },
        "models": {"providers": {"anthropic": {
            "baseUrl": METERED_PROVIDER_BASE_URL,
            "auth": "api-key",
            "api": "anthropic-messages",
            "agentRuntime": {"id": "openclaw"},
            "maxTokens": 8000,
            "timeoutSeconds": 180,
        }}},
        "agents": {
            "entries": {"supervisor": {
                "name": "Journal plan maintenance",
                "runtime": {"type": "embedded"},
                "model": {"primary": "anthropic/claude-sonnet-5", "fallbacks": []},
                "modelPolicy": {"allow": ["anthropic/claude-sonnet-5"]},
                "thinkingDefault": "high",
                "models": {"anthropic/claude-sonnet-5": {"agentRuntime": {"id": "openclaw"}, "codeMode": False}},
                "tools": {"allow": expected_tool_names},
            }},
            "defaults": {
                "model": {"primary": "anthropic/claude-sonnet-5"},
                "timeoutSeconds": 180,
                "maxConcurrent": 1,
                "skills": [],
                "embeddedAgent": {"projectSettingsPolicy": "ignore", "cyberFailover": {"mode": "off"}},
                "decisionModel": "",
                "utilityModel": "anthropic/claude-sonnet-5",
            },
        },
        "hooks": {
            "enabled": False,
            "token": "INERT-FIXTURE-NOT-A-CREDENTIAL-REPLACE-OFFLINE",
            "path": "/hooks",
            "allowedAgentIds": ["supervisor"],
            "allowRequestSessionKey": False,
        },
        "mcp": {"servers": {"journal": {
            "enabled": False,
            "transport": "stdio",
            "command": "/opt/journal-supervisor/bin/journal-supervisor-bridge",
            "args": ["mcp"],
            "connectionTimeoutMs": 5000,
            "requestTimeoutMs": 20000,
            "supportsParallelToolCalls": False,
            "toolFilter": {"include": list(TOOL_NAMES)},
        }}},
        "tools": {"allow": expected_tool_names},
    }
    if fixture.get("openclaw_config") != expected_config:
        raise ContractError("complete OpenClaw configuration differs from the pinned closed fixture")
    expected_job = {
        "name": "journal-supervisor-reconcile-v1",
        "agentId": "supervisor",
        "enabled": False,
        "schedule": {"kind": "every", "everyMs": 300000},
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "command",
            "argv": ["/opt/journal-supervisor/bin/journal-supervisor-bridge", "reconcile"],
            "timeoutSeconds": 45,
            "noOutputTimeoutSeconds": 30,
            "outputMaxBytes": 16384,
        },
        "delivery": {"mode": "none"},
        "failureAlert": False,
    }
    if fixture.get("cron_add_params") != expected_job:
        raise ContractError("complete cron.add command differs from the pinned bounded fixture")
    expected_hook = {
        "message": "Resolve only the journal-issued run reference example-run using journal_supervisor.observe; evidence and authority come from journal.",
        "name": "Journal supervision admission",
        "agentId": "supervisor",
        "sessionMode": "isolated",
        "deliver": False,
        "thinking": "high",
        "model": "anthropic/claude-sonnet-5",
        "timeoutSeconds": 180,
    }
    if fixture.get("hook_agent_request") != expected_hook:
        raise ContractError("complete private hook request differs from the pinned reference-only fixture")
    if fixture.get("hook_headers_without_secrets") != {
        "Content-Type": "application/json",
        "Idempotency-Key": "example-run",
    }:
        raise ContractError("hook headers must contain only content type and run idempotency")
