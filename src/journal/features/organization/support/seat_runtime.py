"""The small, provider-neutral OpenRig boundary used by organization workers."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable

from journal.config import Config
from journal.features.organization.support.usage_ledger import UsageReading
from journal.features.workers.organization_options import OrganizationOptions
from journal.providers.support.helper_setup import JOURNAL_ACTIVE
from journal.repositories.setting_rows import SettingRows
from journal.support.agent_token import AgentToken
from journal.support.caller import ACTOR, ACTOR_TOKEN, AGENT_SHELL, ORGANIZATION_SEAT, Caller
from journal.support.rejection import Rejection


VERSION = re.compile(r"\b(\d+\.\d+\.\d+)\b")
SESSION_FIELDS = {
    "claude": ("sessionId", "session_id"),
    "codex": ("threadId", "thread_id", "conversation_id", "sessionId", "session_id"),
}
PID_FIELDS = ("pid", "processPid", "process_pid", "nativePid", "native_pid", "observedPid")
STATUS_FIELDS = ("sessionStatus", "session_status", "status")


@dataclass(frozen=True)
class SeatAddress:
    pod: str
    member: str


@dataclass(frozen=True)
class SeatMember:
    rig: str
    openrig_version: str
    pod: str
    member: str
    logical_id: str
    target: str
    provider: str
    model: str
    runtime: str
    actor: str
    token: str
    environment: str
    root: str
    path: str
    active: str
    agent_shell: str
    organization_seat: str = ""


@dataclass(frozen=True)
class SeatSession:
    pid: int
    session: str
    status: str
    status_updated_at: float
    activity_status: str = "unknown"


class SeatRuntime:
    """Consume the selected-provider spec; it does not generate rig or agent specs."""

    def __init__(self, config: Config, settings: SettingRows, execute: Callable = subprocess.run) -> None:
        self.config, self.settings, self.execute = config, settings, execute

    def roster(self, rig: str) -> tuple[SeatAddress, ...]:
        spec = self.read_spec(rig)
        return tuple(
            SeatAddress(str(pod.get("id", "")), str(member.get("id", "")))
            for pod in spec.get("pods", []) if isinstance(pod, dict)
            for member in pod.get("members", []) if isinstance(member, dict) and member.get("id")
        )

    @staticmethod
    def target(rig: str, pod: str, member: str) -> str:
        return f"{pod}-{member}@{rig}"

    def spec_folder(self, rig: str) -> Path:
        return self.config.home / "runtime" / "rigs" / rig

    def read_spec(self, rig: str) -> dict:
        path = self.spec_folder(rig) / "rig.yaml"
        if not path.is_file():
            raise Rejection(f"OpenRig spec for {rig} is missing at {path}")
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError) as failed:
            raise Rejection(f"OpenRig spec for {rig} cannot be read: {failed}") from failed
        if not isinstance(spec, dict):
            raise Rejection(f"OpenRig spec for {rig} is not an object")
        return spec

    def member(self, rig: str, pod: str, member: str, selected_provider: str = "") -> SeatMember:
        folder = self.spec_folder(rig)
        spec = self.read_spec(rig)
        for placed in spec.get("pods", []):
            if placed.get("id") != pod:
                continue
            for candidate in placed.get("members", []):
                if candidate.get("id") != member:
                    continue
                environment = candidate.get("env", {})
                provider = str(candidate.get("provider", candidate.get("selected_provider", selected_provider))).lower()
                model = str(candidate.get("model", ""))
                runtime = str(candidate.get("runtime", ""))
                self.generated_boundary(folder, candidate, provider, runtime)
                return SeatMember(
                    rig, str(spec.get("openrig_version", spec.get("openrigVersion", ""))), pod, member,
                    f"{pod}.{member}", self.target(rig, pod, member), provider, model, runtime,
                    str(environment.get(ACTOR, "")), str(environment.get(ACTOR_TOKEN, "")),
                    str(environment.get("JOURNAL_ENV", "")), str(environment.get("JOURNAL_ROOT", "")),
                    str(environment.get("PATH", "")), str(environment.get(JOURNAL_ACTIVE, "")),
                    str(environment.get(AGENT_SHELL, "")), str(environment.get(ORGANIZATION_SEAT, "")),
                )
        raise Rejection(f"OpenRig spec for {rig} has no seat {pod}.{member}")

    def organization_member(self, rig: str, identity: str, provider: str) -> SeatMember:
        for address in self.roster(rig):
            member = self.member(rig, address.pod, address.member, provider)
            if member.organization_seat == identity:
                return member
        raise Rejection(f"OpenRig rig {rig} has no organization seat {identity}")

    def member_for_caller(self, caller: Caller) -> SeatMember:
        if not caller.organization_seat or not caller.organization_rig or not caller.actor_token:
            raise Rejection("organization handoff and inbox run only from a generated organization seat")
        member = self.organization_member(caller.organization_rig, caller.organization_seat, caller.provider or "")
        if (member.token != caller.actor_token or member.environment != caller.environment or member.provider != caller.provider
                or member.root != str(self.config.root)):
            raise Rejection("this journal command does not match its generated organization seat")
        return member

    def generated_boundary(self, folder: Path, member: dict, provider: str, runtime: str) -> None:
        if not provider or not runtime:
            raise Rejection("OpenRig seat spec does not identify its selected provider and runtime")
        agent_ref = str(member.get("agent_ref", ""))
        agent_name = agent_ref.removeprefix("local:agents/")
        if not agent_name:
            raise Rejection("OpenRig seat spec does not identify its generated agent")
        agent = folder / "agents" / agent_name
        try:
            agent_spec = json.loads((agent / "agent.yaml").read_text())
        except (OSError, ValueError) as failed:
            raise Rejection(f"OpenRig seat {agent_name} is missing its generated selected-provider agent spec: {failed}") from failed
        resources = agent_spec.get("resources", {}).get("runtime_resources", [])
        if agent_spec.get("defaults", {}).get("runtime", runtime) != runtime:
            raise Rejection(f"OpenRig seat {agent_name} does not use its generated selected-provider runtime {runtime}")
        selected_hooks = [resource for resource in resources if "journal" in str(resource.get("id", "")).lower() and resource.get("runtime", runtime) == runtime]
        skill_ids = self.profile_skills(agent_spec)
        resource_skills = {str(resource.get("id", "")) for resource in agent_spec.get("resources", {}).get("skills", [])}
        if (not any(self.hook_resource_exists(agent, resource) for resource in selected_hooks)
                or not skill_ids or not set(skill_ids).issubset(resource_skills)):
            raise Rejection(f"OpenRig seat {agent_name} is missing its selected-provider journal hooks or configured skills")
        permissions = [value for key, value in member.items() if key.endswith("_permissions") or key == "permissions"]
        if provider == "codex":
            journal_commands_allowed = any(
                isinstance(value, dict) and value.get("approval") == "never"
                and value.get("sandbox") in {"workspace-write", "read-only"}
                for value in permissions
            )
        else:
            journal_commands_allowed = any("journal" in line.lower() for value in permissions for line in self.strings(value))
        if not journal_commands_allowed:
            raise Rejection(f"OpenRig seat {agent_name} is missing journal helper commands in its provider permissions")

    @staticmethod
    def hook_resource_exists(agent: Path, resource: dict) -> bool:
        path = str(resource.get("path", ""))
        return bool(path and (agent / path).is_file()) or any(resource.get(key) for key in ("settings", "flags", "value"))

    @staticmethod
    def profile_skills(agent_spec: dict) -> list:
        profiles = agent_spec.get("profiles", {})
        return [skill for profile in profiles.values() if isinstance(profile, dict)
                for skill in profile.get("uses", {}).get("skills", [])]

    @classmethod
    def strings(cls, value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for child in value.values():
                yield from cls.strings(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                yield from cls.strings(child)

    def worker_token(self, member: SeatMember, provider: str, model: str, actor: str, environment: str) -> AgentToken:
        first_path = member.path.split(os.pathsep)[0]
        if (member.provider != provider or member.model != model or member.actor != actor
                or member.environment != environment or not member.token or member.root != str(self.config.root)
                or first_path != str(self.config.home / "bin") or member.active != "1" or member.agent_shell != "1"):
            raise Rejection(f"OpenRig seat {member.logical_id} mismatch: {provider}/{model}, worker {actor}, journal environment")
        return AgentToken(member.token)

    def version(self) -> str:
        result = self.run("--version", check=False)
        found = VERSION.search(result.stdout or result.stderr)
        if result.returncode or found is None:
            raise Rejection(f"could not read the installed OpenRig version: {(result.stderr or result.stdout).strip()}")
        return found.group(1)

    def check_version(self, spec_version: str = "") -> str:
        installed = self.version()
        expected = str(self.settings.option(OrganizationOptions.OPENRIG_VERSION) or spec_version or "").strip()
        if expected and installed != expected:
            raise Rejection(f"OpenRig is {installed}; workers.openrig_version requires {expected}")
        return installed

    def status(self, seat: SeatMember | str) -> dict:
        target = seat.target if isinstance(seat, SeatMember) else seat
        result = self.run("seat", "status", target, "--json")
        status = self.object(result.stdout)
        if isinstance(seat, SeatMember):
            # OpenRig 0.7.5 puts freshness on the node's agentActivity.sampledAt,
            # exposed by the full node listing rather than seat status.
            node = self.node(seat)
            if node:
                return {**status, **node}
        return status

    def node(self, seat: SeatMember) -> dict:
        result = self.run("ps", "--nodes", "--full", "--json", "--rig", seat.rig, check=False)
        if result.returncode:
            return {}
        rows = self.objects(self.json_value(result.stdout))
        identifiers = {seat.target, seat.logical_id, f"{seat.pod}.{seat.member}", seat.member, f"{seat.pod}-{seat.member}"}
        return next((value for value in rows if any(str(value.get(key, "")) in identifiers for key in ("name", "id", "logicalId", "logical_id", "seat", "sessionName"))), {})

    def expected_seats(self, rig: str) -> int | None:
        path = self.config.home / "runtime" / "rigs" / rig / "rig.yaml"
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError):
            return None
        members = [member for pod in spec.get("pods", []) for member in pod.get("members", [])]
        return len(members) or None

    def session(self, seat: SeatMember, native_session: str = "") -> SeatSession | None:
        try:
            status = self.status(seat)
        except Rejection:
            status = {}
        objects = self.objects(status)
        field_order = SESSION_FIELDS.get(seat.provider, ()) + ("sessionId", "session_id", "threadId", "thread_id", "conversation_id", "session")
        found_session = next((str(value[key]) for value in objects for key in field_order if value.get(key)), "")
        pid = next((int(value[key]) for value in objects for key in PID_FIELDS if str(value.get(key, "")).isdigit() and int(value[key]) > 0), 0)
        if not found_session or not pid:
            node = self.node(seat)
            node_rows = list(self.objects(node))
            if not found_session:
                found_session = next((str(value[key]) for value in node_rows for key in field_order if value.get(key)), "")
            if not pid:
                pid = next((int(value[key]) for value in node_rows for key in PID_FIELDS if str(value.get(key, "")).isdigit() and int(value[key]) > 0), 0)
            status = {**status, **node}
            objects = self.objects(status)
        if native_session and found_session and native_session != found_session:
            return None
        session = native_session or found_session
        if not session or not pid:
            return None
        status_name = self.session_status(status)
        activity, updated = self.activity_status(status)
        return SeatSession(pid, session, status_name, updated, activity)

    def send(self, seat: SeatMember, text: str) -> None:
        self.run("send", seat.target, text, "--json")

    def start_rig(self, spec: Path) -> None:
        self.run("up", str(spec), "--json")

    def replace_rig(self, rig: str, spec: Path) -> None:
        self.run("down", rig, "--yes", "--json")
        self.start_rig(spec)

    def rig_exists(self, rig: str) -> bool:
        return self.run("ps", "--nodes", "--json", "--rig", rig, check=False).returncode == 0

    def expand(self, rig: str, pod: Path, root: Path) -> None:
        self.run("expand", rig, str(pod), "--json", "--rig-root", str(root))

    def add(self, rig: str, pod: str, member: Path, root: Path) -> None:
        self.run("add", rig, pod, str(member), "--json", "--rig-root", str(root))

    def remove_node(self, rig: str, logical_id: str) -> None:
        self.run("remove", rig, logical_id, "--json")

    def edge(self, rig: str, source: str, target: str) -> None:
        self.run("edge", "add", rig, source, target, "--kind", "delegates_to", "--json")

    def queue_items(self) -> tuple[dict, ...]:
        result = self.run("queue", "list", "--all", "--all-rigs", "--full", "--json")
        return tuple(value for value in self.objects(self.object(result.stdout))
                     if (value.get("qitemId") or value.get("id"))
                     and isinstance(value.get("source"), str) and isinstance(value.get("destination"), str))

    def queue_transitions(self) -> tuple[dict, ...]:
        rows = []
        cursor = ""
        seen = set()
        while True:
            arguments = ("telemetry", "transitions", "--start", "retained", "--json") if not cursor else ("telemetry", "transitions", "--cursor", cursor, "--json")
            payload = self.object(self.run(*arguments).stdout)
            rows.extend(value for value in self.objects(payload) if value.get("qitemId"))
            page = payload.get("page")
            if not isinstance(page, dict) or page.get("hasMore") is not True:
                return tuple(rows)
            next_cursor = page.get("nextCursor")
            if not isinstance(next_cursor, str) or not next_cursor or next_cursor in seen:
                raise Rejection("OpenRig queue transitions have another page but no usable next cursor")
            seen.add(next_cursor)
            cursor = next_cursor

    def launch(self, seat: SeatMember, reason: str) -> None:
        self.run("seat", "launch", seat.target, "--fresh", "--stop", "--reason", reason, "--operator", "journal", "--json")

    def stop(self, seat: SeatMember | str, reason: str) -> None:
        target = seat.target if isinstance(seat, SeatMember) else seat
        self.run("seat", "stop", target, "--reason", reason, "--operator", "journal", "--json")

    def usage_cost(self, seat: SeatMember | str) -> UsageReading:
        target = seat.target if isinstance(seat, SeatMember) else seat
        try:
            result = self.run("usage", "cost", "--seat", target, "--json", check=False)
        except Rejection as failed:
            return self.unavailable_cost(str(failed))
        if result.returncode:
            return self.unavailable_cost((result.stderr or result.stdout or "OpenRig did not report usage cost").strip())
        try:
            payload = self.object(result.stdout)
        except Rejection as failed:
            return self.unavailable_cost(str(failed))
        seats = payload.get("seats")
        if not isinstance(seats, list):
            return self.unavailable_cost("the response has no per-seat cost list")
        record = next((row for row in seats if isinstance(row, dict) and row.get("seatSession") == target), None)
        if record is None:
            return self.unavailable_cost(f"OpenRig did not report seat {target}")
        kind = record.get("kind") if isinstance(record.get("kind"), str) else "unknown"
        source = record.get("source") if isinstance(record.get("source"), str) and record["source"] else "not reported"
        source_status = record.get("status") if isinstance(record.get("status"), str) and record["status"] else "unknown"
        raw_window = record.get("window")
        window = raw_window if isinstance(raw_window, dict) else {}
        native_session_id = window.get("nativeSessionId", record.get("nativeSessionId", ""))
        freshness = "stale" if record.get("stale") is True else "fresh" if record.get("stale") is False else "unknown"
        amount = record.get("costUsd")
        unavailable_statuses = {"unknown", "unavailable", "not_reported", "not reported", "no_cost", "missing"}
        usable_amount = (float(amount) if isinstance(amount, (int, float)) and not isinstance(amount, bool)
                         and math.isfinite(float(amount)) and float(amount) >= 0
                         and source_status.strip().lower() not in unavailable_statuses else None)
        status = ("stale" if usable_amount is not None and freshness == "stale"
                  else "estimated" if usable_amount is not None and freshness == "fresh" else "unavailable")
        coverage_value = record.get("coverage")
        coverage = (coverage_value if isinstance(coverage_value, str) and coverage_value else
                    json.dumps(coverage_value, sort_keys=True) if coverage_value is not None else "not reported")
        return UsageReading(
            usable_amount,
            source,
            kind,
            str(native_session_id or ""),
            dict(window),
            coverage,
            freshness if freshness != "unknown" else "unavailable",
            status,
            source_status,
            str(record.get("reason", "")),
            self.timestamp(window.get("asOf")),
        )

    @staticmethod
    def unavailable_cost(reason: str) -> UsageReading:
        return UsageReading(None, "OpenRig rig usage cost --json", "unknown", "", {}, "not reported",
                            "unavailable", "unavailable", "unavailable", reason)

    @staticmethod
    def timestamp(value: object) -> float | None:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return float(value)
        except ValueError:
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.timestamp()

    @staticmethod
    def session_status(status: dict) -> str:
        return next((found.lower() for value in SeatRuntime.objects(status) for key in STATUS_FIELDS
                     if isinstance((found := value.get(key)), str)), "unknown")

    @staticmethod
    def activity_status(status: dict) -> tuple[str, float]:
        sampled = next((activity for value in SeatRuntime.objects(status)
                        if isinstance((activity := value.get("agentActivity")), dict)
                        and isinstance(activity.get("state"), str)), None)
        state = str(sampled["state"]).lower() if sampled else SeatRuntime.session_status(status)
        return state, SeatRuntime.status_updated_at(status)

    @staticmethod
    def status_updated_at(status: dict) -> float:
        values = list(SeatRuntime.objects(status))
        timestamps = [activity.get("sampledAt") for value in values
                      if isinstance((activity := value.get("agentActivity")), dict) and not activity.get("stale")]
        timestamps.extend(value.get(key) for value in values
                          for key in ("statusUpdatedAt", "status_updated_at", "updatedAt", "updated_at"))
        for value in timestamps:
            if isinstance(value, (int, float)):
                return float(value)
            if not isinstance(value, str) or not value.strip():
                continue
            try:
                return float(value)
            except ValueError:
                try:
                    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    return parsed.timestamp()
                except ValueError:
                    continue
        return 0.0

    @staticmethod
    def objects(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from SeatRuntime.objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from SeatRuntime.objects(child)

    def run(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        if shutil.which("rig") is None:
            raise Rejection("OpenRig's rig command is not on PATH")
        try:
            result = self.execute(["rig", *arguments], capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired) as failed:
            raise Rejection(f"OpenRig {' '.join(arguments)} failed: {failed}") from failed
        if check and result.returncode and not self.already_stopped(arguments, result):
            raise Rejection(f"OpenRig {' '.join(arguments)} failed: {(result.stderr or result.stdout).strip()}")
        return result

    @staticmethod
    def already_stopped(arguments: tuple[str, ...], result: subprocess.CompletedProcess) -> bool:
        if not arguments or arguments[0] != "down":
            return False
        try:
            response = json.loads(result.stdout)
        except ValueError:
            return False
        return (not result.stderr.strip() and isinstance(response, dict) and response.get("alreadyStopped") is True
                and not response.get("errors") and not response.get("error"))

    @staticmethod
    def json_value(output: str) -> object:
        try:
            return json.loads(output)
        except ValueError as failed:
            raise Rejection(f"OpenRig returned invalid JSON: {failed}") from failed

    @staticmethod
    def object(output: str) -> dict:
        value = SeatRuntime.json_value(output)
        if not isinstance(value, dict):
            raise Rejection("OpenRig returned a JSON value other than an object")
        return value
