import json
from io import BytesIO
import os
import subprocess
from copy import deepcopy
from pathlib import Path


class SimulatedSeats:
    """Answer OpenRig calls in memory for one lab run."""

    def __init__(self) -> None:
        self.pid = os.getpid()
        self.version = "0.7.6"
        self.cli_version = "0.7.6"
        self.calls: list[tuple[str, ...]] = []
        self.rigs: set[str] = set()
        self.stopped_rigs: set[str] = set()
        self.specs: dict[str, dict] = {}
        self.sessions: dict[str, dict[str, object]] = {}
        self.environments: dict[str, dict[str, str]] = {}
        self.messages: list[tuple[str, str]] = []
        self.session_number = 0
        self.attention: dict[str, str] = {}
        self.next_attention_reason = ""
        self.health_requests: list[tuple[str, int]] = []

    def health_request(self, url: str, timeout: int = 3) -> BytesIO:
        self.health_requests.append((url, timeout))
        return BytesIO(json.dumps({"semver": self.version}).encode())

    def run(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        self.calls.append(arguments)
        if arguments == ("--version",):
            return self.result(arguments, f"OpenRig {self.cli_version}\n")
        if arguments[0] == "up":
            path = Path(arguments[1])
            rig = path.parent.name
            self.rigs.add(rig)
            self.stopped_rigs.discard(rig)
            self.specs[rig] = json.loads(path.read_text())
            self.start_members(rig, self.specs[rig])
            reason = self.next_attention_reason or self.project_mcp_attention(path.parent, self.specs[rig])
            self.next_attention_reason = ""
            if reason:
                self.attention[rig] = reason
                return self.result(arguments, json.dumps({
                    "status": "partial",
                    "results": [{"step": "import_rig", "status": "blocked", "code": "attention_required", "reason": reason}],
                }), 1)
            return self.result(arguments, "{}")
        if arguments[0] == "down":
            rig = arguments[1]
            if rig in self.stopped_rigs:
                return self.result(arguments, '{"alreadyStopped": true, "errors": []}', 1)
            if rig not in self.rigs:
                return self.result(arguments, '{"error": "unknown rig"}', 1)
            self.stopped_rigs.add(rig)
            for target in self.sessions:
                if target.endswith(f"@{rig}"):
                    self.stop_session(target)
            return self.result(arguments, "{}")
        if arguments[0] == "ps":
            return self.processes(arguments)
        if arguments[:2] == ("seat", "status"):
            return self.result(arguments, json.dumps(self.sessions.get(arguments[2], {})))
        if arguments[:2] == ("seat", "launch"):
            self.start_session(arguments[2], self.environment_for(arguments[2]))
            return self.result(arguments, "{}")
        if arguments[:2] == ("seat", "stop"):
            self.stop_session(arguments[2])
            return self.result(arguments, "{}")
        if arguments[0] == "send":
            self.messages.append((arguments[1], arguments[2]))
            return self.result(arguments, "{}")
        if arguments[0] == "expand":
            rig, path = arguments[1], Path(arguments[2])
            pod = json.loads(path.read_text())
            self.specs[rig].setdefault("pods", []).append(pod)
            self.start_expanded_pod(rig, pod)
            return self.result(arguments, "{}")
        if arguments[0] == "add":
            rig, pod_id, path = arguments[1], arguments[2], Path(arguments[3])
            member = json.loads(path.read_text())
            pod = next(pod for pod in self.specs[rig]["pods"] if pod["id"] == pod_id)
            pod.setdefault("members", []).append(member)
            self.start_session(f"{pod_id}-{member['id']}@{rig}", member.get("env", {}))
            return self.result(arguments, "{}")
        if arguments[0] == "launch":
            target = f"{arguments[2]}@{arguments[1]}"
            self.start_session(target, self.environment_for(target))
            return self.result(arguments, "{}")
        if arguments[0] == "usage":
            return self.result(arguments, '{"seats": []}')
        if arguments[:2] == ("queue", "list"):
            return self.result(arguments, "{}")
        if arguments[:2] == ("telemetry", "transitions"):
            return self.result(arguments, '{"transitions": [], "page": {"hasMore": false}}')
        if arguments[0] == "remove":
            rig, logical_id = arguments[1:3]
            pod_id, member_id = logical_id.split(".", 1)
            pod = next(pod for pod in self.specs[rig]["pods"] if pod["id"] == pod_id)
            pod["members"] = [member for member in pod["members"] if member["id"] != member_id]
            pod["edges"] = [edge for edge in pod.get("edges", []) if member_id not in (edge.get("from"), edge.get("to"))]
            self.specs[rig]["edges"] = [edge for edge in self.specs[rig].get("edges", []) if logical_id not in (edge.get("from"), edge.get("to"))]
            target = f"{pod_id}-{member_id}@{rig}"
            self.sessions.pop(target, None)
            self.environments.pop(target, None)
            return self.result(arguments, "{}")
        if arguments[0] == "edge":
            return self.result(arguments, "{}")
        return self.result(arguments, "", 2, f"unsupported simulated OpenRig call: {' '.join(arguments)}")

    @staticmethod
    def project_mcp_attention(folder: Path, spec: dict) -> str:
        for pod in spec.get("pods", []):
            for member in pod.get("members", []):
                if member.get("runtime") != "claude-code":
                    continue
                project_mcp = Path(member.get("cwd", "")) / ".mcp.json"
                try:
                    servers = json.loads(project_mcp.read_text()).get("mcpServers", {})
                except (OSError, ValueError):
                    continue
                if not servers or SimulatedSeats.project_mcp_servers_selected(folder, member):
                    continue
                return f"OpenRig seat {pod['id']}.{member['id']} needs approval for project MCP servers"
        return ""

    @staticmethod
    def project_mcp_servers_selected(folder: Path, member: dict) -> bool:
        agent_name = str(member.get("agent_ref", "")).removeprefix("local:agents/")
        try:
            agent = json.loads((folder / "agents" / agent_name / "agent.yaml").read_text())
        except (OSError, ValueError):
            return False
        profiles = agent.get("profiles", {})
        resources = agent.get("resources", {}).get("runtime_resources", [])
        selected = {
            resource
            for profile in profiles.values() if isinstance(profile, dict)
            for resource in profile.get("uses", {}).get("runtime_resources", [])
        }
        for resource in resources:
            if resource.get("id") not in selected or resource.get("type") != "claude_settings_fragment":
                continue
            try:
                settings = json.loads((folder / "agents" / agent_name / resource["path"]).read_text())
            except (OSError, ValueError):
                continue
            if settings.get("enableAllProjectMcpServers") is True:
                return True
        return False

    def execute(self, command: list[str], **kwargs) -> subprocess.CompletedProcess:
        return self.run(*command[1:], check=False)

    def remember_spec(self, rig: str, path: Path) -> None:
        self.specs[rig] = json.loads(path.read_text())

    def member_environment(self, rig: str, pod: str, member: str) -> dict[str, str]:
        return self.environments[f"{pod}-{member}@{rig}"]

    def copied(self) -> "SimulatedSeats":
        return deepcopy(self)

    def start_members(self, rig: str, spec: dict) -> None:
        for pod in spec.get("pods", []):
            for member in pod.get("members", []):
                self.start_session(f"{pod['id']}-{member['id']}@{rig}", member.get("env", {}))

    def start_expanded_pod(self, rig: str, pod: dict) -> None:
        environment = self.specs[rig].get("env", {})
        for member in pod.get("members", []):
            self.start_session(f"{pod['id']}-{member['id']}@{rig}", environment)

    def processes(self, arguments: tuple[str, ...]) -> subprocess.CompletedProcess:
        rig = self.argument(arguments, "--rig")
        if rig not in self.rigs:
            return self.result(arguments, "[]", 1, f"simulated rig {rig} is not running")
        rows = [
            {"name": target, **session}
            for target, session in self.sessions.items()
            if target.endswith(f"@{rig}")
        ]
        return self.result(arguments, json.dumps(rows))

    def start_session(self, target: str, environment: dict[str, str] | None = None) -> None:
        self.session_number += 1
        self.sessions[target] = {
            "sessionId": f"sim-{self.session_number}",
            "pid": self.pid,
            "status": "running",
            "statusUpdatedAt": 1_800_000_000,
        }
        self.environments[target] = dict(environment or {})

    def environment_for(self, target: str) -> dict[str, str]:
        address, rig = target.rsplit("@", 1)
        return next(
            member.get("env", {})
            for pod in self.specs[rig]["pods"]
            for member in pod["members"]
            if f"{pod['id']}-{member['id']}" == address
        )

    def idle(self, target: str) -> None:
        self.sessions[target]["status"] = "idle"

    def stop_session(self, target: str) -> None:
        if target in self.sessions:
            self.sessions[target].update(pid=0, status="stopped")

    def forget_rig(self, rig: str) -> None:
        self.rigs.discard(rig)
        self.stopped_rigs.discard(rig)
        self.specs.pop(rig, None)
        for target in tuple(self.sessions):
            if target.endswith(f"@{rig}"):
                self.sessions.pop(target)
                self.environments.pop(target, None)

    @staticmethod
    def argument(arguments: tuple[str, ...], name: str) -> str:
        try:
            return arguments[arguments.index(name) + 1]
        except (ValueError, IndexError):
            return ""

    @staticmethod
    def result(arguments: tuple[str, ...], output: str, code: int = 0, error: str = "") -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(["rig", *arguments], code, output, error)
