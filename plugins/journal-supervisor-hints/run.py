#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


def answer(line: dict) -> str:
    root = Path(os.environ["JOURNAL_ROOT"])
    sys.path.insert(0, str(root / "src"))
    from supervisor_bridge.hints import HintError, HintSpool

    try:
        response = HintSpool(Path(os.environ["JOURNAL_PLUGIN_DATA"]) / "transport").enqueue_event_line(json.dumps(line, separators=(",", ":")))
    except HintError:
        response = {"v": 1, "answer": "allow"}
    return json.dumps(response, separators=(",", ":"))


if __name__ == "__main__":
    try:
        print(answer(json.loads(sys.stdin.readline())))
    except (KeyError, json.JSONDecodeError, OSError):
        print(json.dumps({"v": 1, "answer": "allow"}))
