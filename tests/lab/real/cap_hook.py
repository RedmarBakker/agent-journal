import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen


def forward(path: Path, firing: str) -> None:
    hook = json.loads(path.read_text(encoding="utf-8"))
    kind = hook.get("hook_event_name")
    if kind not in {"SessionStart", "SessionEnd", "UserPromptSubmit"}:
        return
    session_id = hook.get("session_id")
    agent_id = hook.get("agent_id")
    if isinstance(agent_id, str) and agent_id:
        session_id = f"{session_id}:{agent_id}"
    body = json.dumps({"event": kind, "session_id": session_id, "firing": firing}).encode()
    request = Request(os.environ["JOURNAL_LAB_CAP_URL"], data=body, headers={
        "Content-Type": "application/json", "X-Run-Cap-Token": os.environ["JOURNAL_LAB_CAP_TOKEN"],
    })
    with urlopen(request, timeout=5) as response:
        if response.status != 200:
            raise ValueError("run cap event was refused")


if __name__ == "__main__":
    forward(Path(sys.argv[1]), sys.argv[2])
