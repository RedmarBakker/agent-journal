#!/usr/bin/env python3
import argparse
import fcntl
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from supervisor_bridge.proposal_evaluation import load_case, result_row


PROFILE = ROOT / "docs/supervisor/v1"
COMPOSE = PROFILE / "compose.json"
ENV_FILE = PROFILE / "live-smoke.env"
DEFAULT_RESULTS = PROFILE / "proposal-evaluation-results.jsonl"


def parse_args():
    parser = argparse.ArgumentParser(description="Append one raw supervisor proposal result row.")
    parser.add_argument("case_id")
    parser.add_argument("--bridge-state", type=Path)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--env-file", type=Path, default=ENV_FILE)
    return parser.parse_args()


def writer_rows(env_file: Path) -> list[dict]:
    result = subprocess.run(
        ["docker", "compose", "--project-name", "journal-supervisor-smoke", "--env-file", str(env_file),
         "-f", str(COMPOSE), "--profile", "authorized-staging", "exec", "--user", "journal", "-T",
         "writer", "/usr/local/bin/supervisor-proposal-writer-rows"],
        check=True, capture_output=True, text=True,
    )
    payload = json.loads(result.stdout)
    if set(payload) != {"rows"} or not isinstance(payload["rows"], list):
        raise ValueError("writer returned an unexpected supervisor row export")
    return payload["rows"]


def bridge_state_path(env_file: Path) -> Path:
    values = [line.split("=", 1)[1] for line in env_file.read_text().splitlines() if line.startswith("GATEWAY_STATE_PATH=")]
    if len(values) != 1 or not values[0].startswith("/"):
        raise ValueError("live-smoke.env must name one absolute GATEWAY_STATE_PATH")
    return Path(values[0]) / "journal-supervisor-transport" / "bridge-state.json"


def append_once(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    os.fchmod(descriptor, 0o600)
    with os.fdopen(descriptor, "r+", encoding="utf-8") as output:
        fcntl.flock(output.fileno(), fcntl.LOCK_EX)
        output.seek(0)
        for line in output:
            prior = json.loads(line)
            if prior.get("case") == row["case"]:
                raise ValueError(f"case {row['case']} already has a raw result row")
        output.seek(0, 2)
        output.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        output.flush()


def main():
    args = parse_args()
    load_case(PROFILE / "proposal-evaluation-cases-v1.json", args.case_id)
    bridge_path = args.bridge_state or bridge_state_path(args.env_file)
    bridge_state = json.loads(bridge_path.read_text(encoding="utf-8"))
    row = result_row(args.case_id, bridge_state, writer_rows(args.env_file))
    append_once(args.results, row)
    print(f"appended raw result for {args.case_id}: {row['outcome']['action_status'] or row['outcome']['admission']}")


if __name__ == "__main__":
    main()
