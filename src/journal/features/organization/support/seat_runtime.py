"""The small, provider-neutral OpenRig boundary used by organization workers."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable

from journal.config import Config
from journal.features.workers.organization_options import OrganizationOptions
from journal.providers.support.helper_setup import JOURNAL_ACTIVE
from journal.repositories.setting_rows import SettingRows
from journal.support.agent_token import AgentToken
from journal.support.caller import ACTOR, ACTOR_TOKEN, AGENT_SHELL
from journal.support.rejection import Rejection


VERSION = re.compile(r"\b(\d+\.\d+\.\d+)\b")
SESSION_FIELDS = {
    "claude": ("sessionId", "session_id"),
    "codex": ("threadId", "thread_id", "conversation_id", "sessionId", "session_id"),
}
PID_FIELDS = ("pid", "processPid", "process_pid", "nativePid", "native_pid")
STATUS_FIELDS = ("sessionStatus", "session_status", "status")


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

    def member(self, rig: str, pod: str, member: str, selected_provider: str = "") -> SeatMember:
        folder = self.config.home / "runtime" / "rigs" / rig
        path = folder / "rig.yaml"
        if not path.is_file():
            raise Rejection(f"OpenRig spec for {rig} is missing at {path}")
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError) as failed:
            raise Rejection(f"OpenRig spec for {rig} cannot be read: {failed}") from failed
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
                    f"{pod}.{member}", f"{pod}-{member}@{rig}", provider, model, runtime,
                    str(environment.get(ACTOR, "")), str(environment.get(ACTOR_TOKEN, "")),
                    str(environment.get("JOURNAL_ENV", "")), str(environment.get("JOURNAL_ROOT", "")),
                    str(environment.get("PATH", "")), str(environment.get(JOURNAL_ACTIVE, "")),
                    str(environment.get(AGENT_SHELL, "")),
                )
        raise Rejection(f"OpenRig spec for {rig} has no seat {pod}.{member}")

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
            raise Rejection(f"OpenRig seat {member.logical_id} does not match the selected {provider} model {model}, worker {actor}, and journal environment")
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
        rows = self.objects(self.object(result.stdout))
        identifiers = {seat.target, seat.logical_id, f"{seat.pod}.{seat.member}", seat.member, f"{seat.pod}-{seat.member}"}
        return next((value for value in rows if any(str(value.get(key, "")) in identifiers for key in ("name", "id", "logicalId", "logical_id", "seat", "sessionName"))), {})

    def expected_seats(self, rig: str) -> int | None:
        path = self.config.home / "runtime" / "rigs" / rig / "rig.yaml"
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError):
            return None
        members = [member for pod in spec.get("pods", []) for member in pod.get("members", [])]
        roles = [member for member in members if member.get("role") or str(member.get("qualified", "")).startswith("role:")]
        if roles:
            return len(roles)
        roles = [member for member in members if member.get("id") not in {"plan-agent", "domain-agent"}]
        return len(roles) if roles else None

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

    def launch(self, seat: SeatMember, reason: str) -> None:
        self.run("seat", "launch", "--fresh", seat.target, "--reason", reason, "--operator", "journal", "--json")

    def stop(self, seat: SeatMember | str, reason: str) -> None:
        target = seat.target if isinstance(seat, SeatMember) else seat
        self.run("seat", "stop", target, "--reason", reason, "--operator", "journal", "--json")

    def cumulative_cost(self, seat: SeatMember | str) -> float | None:
        target = seat.target if isinstance(seat, SeatMember) else seat
        result = self.run("usage", "cost", "--seat", target, "--json", check=False)
        if result.returncode:
            return None
        try:
            value = self.object(result.stdout)
            cost = value.get("cost", value)
            total = cost.get("total_cost_usd") if isinstance(cost, dict) else None
            return float(total) if total is not None else None
        except (Rejection, TypeError, ValueError):
            return None

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
        if check and result.returncode:
            raise Rejection(f"OpenRig {' '.join(arguments)} failed: {(result.stderr or result.stdout).strip()}")
        return result

    @staticmethod
    def object(output: str) -> dict:
        try:
            value = json.loads(output)
        except ValueError as failed:
            raise Rejection(f"OpenRig returned invalid JSON: {failed}") from failed
        if not isinstance(value, dict):
            raise Rejection("OpenRig returned a JSON value other than an object")
        return value
