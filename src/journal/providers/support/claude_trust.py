import json
import os
from pathlib import Path


class ClaudeTrust:
    """Claude Code's own record of the folders the person trusts, its state file a constructor value: a launch marks a worktree it made trusted there before Claude Code starts, so the trust question never stops it, as version 3 did."""

    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file

    def trusted(self, folder: Path) -> None:
        state = json.loads(self.state_file.read_text()) if self.state_file.is_file() else {}
        projects = state.setdefault("projects", {})
        if projects.get(str(folder), {}).get("hasTrustDialogAccepted"):
            return
        projects[str(folder)] = {**projects.get(str(folder), {}), "hasTrustDialogAccepted": True}
        written = self.state_file.with_name(f".{self.state_file.name}.{os.getpid()}.journal")
        written.write_text(json.dumps(state, indent=2) + "\n")
        written.replace(self.state_file)
