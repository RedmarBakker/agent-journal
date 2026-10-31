import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path


class SimulatedSeats:
    """Answer OpenRig calls in memory for one lab run."""

    def __init__(self) -> None:
        self.pid = os.getpid()
        self.version = "0.7.6"
        self.calls: list[tuple[str, ...]] = []
        self.rigs: set[str] = set()
        self.stopped_rigs: set[str] = set()
        self.specs: dict[str, dict] = {}
        self.sessions: dict[str, dict[str, object]] = {}
        self.environments: dict[str, dict[str, str]] = {}
        self.messages: list[tuple[str, str]] = []
        self.session_number = 0

    def run(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        self.calls.append(arguments)
        if arguments == ("--version",):
            return self.result(arguments, f"OpenRig {self.version}\n")
        if arguments[0] == "up":
            path = Path(arguments[1])
            rig = path.parent.name
            self.rigs.add(rig)
            self.stopped_rigs.discard(rig)
            self.specs[rig] = json.loads(path.read_text())
            self.start_members(rig, self.specs[rig])
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
        if arguments[0] in {"remove", "edge"}:
            return self.result(arguments, "{}")
        return self.result(arguments, "", 2, f"unsupported simulated OpenRig call: {' '.join(arguments)}")

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

    @staticmethod
    def argument(arguments: tuple[str, ...], name: str) -> str:
        try:
            return arguments[arguments.index(name) + 1]
        except (ValueError, IndexError):
            return ""

    @staticmethod
    def result(arguments: tuple[str, ...], output: str, code: int = 0, error: str = "") -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(["rig", *arguments], code, output, error)
