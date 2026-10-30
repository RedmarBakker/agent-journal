import json
import os
from pathlib import Path
import subprocess


class SimulatedSeats:
    """Answer OpenRig calls in memory for one lab run."""

    def __init__(self) -> None:
        self.pid = os.getpid()
        self.calls: list[tuple[str, ...]] = []
        self.rigs: set[str] = set()
        self.sessions: dict[str, dict[str, object]] = {}
        self.messages: list[tuple[str, str]] = []

    def run(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        self.calls.append(arguments)
        if arguments == ("--version",):
            return self.result(arguments, "OpenRig 0.7.5\n")
        if arguments[0] == "up":
            self.rigs.add(Path(arguments[1]).parent.name)
            return self.result(arguments, "{}")
        if arguments[0] == "ps":
            return self.processes(arguments)
        if arguments[:2] == ("seat", "status"):
            return self.result(arguments, json.dumps(self.sessions.get(arguments[2], {})))
        if arguments[:2] == ("seat", "launch"):
            self.start_session(arguments[2])
            return self.result(arguments, "{}")
        if arguments[:2] == ("seat", "stop"):
            self.stop_session(arguments[2])
            return self.result(arguments, "{}")
        if arguments[0] == "send":
            self.messages.append((arguments[1], arguments[2]))
            return self.result(arguments, "{}")
        if arguments[0] == "launch":
            self.start_session(f"{arguments[2]}@{arguments[1]}")
            return self.result(arguments, "{}")
        if arguments[0] == "usage":
            return self.result(arguments, '{"seats": []}')
        if arguments[:2] == ("queue", "list"):
            return self.result(arguments, "{}")
        if arguments[:2] == ("telemetry", "transitions"):
            return self.result(arguments, '{"transitions": [], "page": {"hasMore": false}}')
        if arguments[0] in {"expand", "add", "remove", "edge"}:
            return self.result(arguments, "{}")
        return self.result(arguments, "", 2, f"unsupported simulated OpenRig call: {' '.join(arguments)}")

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

    def start_session(self, target: str) -> None:
        self.sessions[target] = {
            "sessionId": f"sim-{len(self.sessions) + 1}",
            "pid": self.pid,
            "status": "running",
            "statusUpdatedAt": 1_800_000_000,
        }

    def stop_session(self, target: str) -> None:
        if target in self.sessions:
            self.sessions[target]["status"] = "stopped"

    @staticmethod
    def argument(arguments: tuple[str, ...], name: str) -> str:
        try:
            return arguments[arguments.index(name) + 1]
        except (ValueError, IndexError):
            return ""

    @staticmethod
    def result(arguments: tuple[str, ...], output: str, code: int = 0, error: str = "") -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(["rig", *arguments], code, output, error)
