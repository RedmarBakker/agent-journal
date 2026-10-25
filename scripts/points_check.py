"""The points the running journal recorded for its answers, averaged per endpoint and hook over their recent answers: it passes when every average is at or under the budget, and fails naming each one over it, worst first."""

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

BUDGET_POINTS = 30
ROOT = Path(__file__).resolve().parents[1]


def point_parts() -> dict[str, tuple[int, int]]:
    port = (ROOT / ".journal" / "port").read_text().split()[0]
    with urlopen(Request(f"http://127.0.0.1:{port}/journal/summary"), timeout=20) as answer:
        summary = json.loads(answer.read())
    parts = [part for environment in summary.get("environments", []) for part in ((environment.get("agent") or {}).get("point_parts") or [])]
    return {part["name"]: (part["average"], part["count"]) for part in parts}


def main() -> int:
    parts = point_parts()
    over = sorted(((name, average, count) for name, (average, count) in parts.items() if average > BUDGET_POINTS), key=lambda part: -part[1])
    for name, average, count in over:
        print(f"{name}: {average} points on average over its last {count} answers")
    print(f"{len(parts) - len(over)}/{len(parts)} endpoints and hooks at or under {BUDGET_POINTS} points")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
