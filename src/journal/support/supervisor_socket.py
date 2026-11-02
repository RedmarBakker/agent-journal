import json
import re
import socket
from pathlib import Path

from journal.support.supervisor_reply import SupervisorReply

WAIT_SECONDS = 5.0
PLAN_DRIVER_SUPERVISOR_SOCKET_DIRECTORY = Path("/run/journal-plan-driver-supervisors")
PLAN_DRIVER_SUPERVISOR_SOCKET_GROUP = 10031


class SupervisorSocket:
    """One request to a supervisor on the protocol: a line of JSON out, a line back."""

    @staticmethod
    def plan_driver_path(environment: str) -> Path:
        if not re.fullmatch(r"plan-[1-9][0-9]*", environment):
            raise ValueError("only a numbered Plan environment can use the shared supervisor socket")
        return PLAN_DRIVER_SUPERVISOR_SOCKET_DIRECTORY / f"{environment}.sock"

    @staticmethod
    def ask(path: str, request: dict) -> SupervisorReply:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as link:
            link.settimeout(WAIT_SECONDS)
            link.connect(path)
            link.sendall((json.dumps(request) + "\n").encode())
            return SupervisorReply.parsed(json.loads(link.makefile("rb").readline()))
