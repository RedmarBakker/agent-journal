#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, "/opt/agent-journal/src")

from journal.app import App
from journal.config import Config
from journal.repositories.entries import Entries
from journal.repositories.scope import PROJECT, Scope


ROOT = Path("/data/project")
ENTRY_TYPES = (
    "SupervisorRun",
    "SupervisorRunState",
    "SupervisorUsage",
    "SupervisorObservation",
    "SupervisorEpisode",
    "SupervisorActionState",
    "SupervisorActionReceipt",
    "SupervisorActionReport",
    "SupervisorProposalReceipt",
    "SupervisorProposalDecision",
    "SupervisorWakeup",
)


def main():
    if len(sys.argv) != 1:
        raise SystemExit("this collector accepts no arguments")
    app = App(Config.rooted(ROOT))
    scope = app.container.get(Scope)
    entries = app.container.get(Entries)
    rows = []
    with scope.environment(PROJECT):
        for entry_type in ENTRY_TYPES:
            for row in entries.supervisor_records(entry_type, last=100):
                rows.append({
                    "id": row.row_id,
                    "entry_type": row.entry_type,
                    "created_at": row.created_at.isoformat(),
                    "data": row.data,
                })
    print(json.dumps({"rows": sorted(rows, key=lambda row: row["id"])}, separators=(",", ":")))


if __name__ == "__main__":
    main()
