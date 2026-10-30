import os
import subprocess
import sys
from pathlib import Path

from journal.config import Config
from journal.support.workspace_worktree import WorkspaceWorktree

# the launch switches of an agent nobody sits at: no questions, no browser, no journal of its own
DETACHED = ("--yes", "--no-open", "--no-journal")


class AgentLauncher:
    """Starts an agent for an environment from the running journal: its supervisor runs detached, with no journal of its own and no terminal, and its screen goes to a log under the runtime folder; in a worktree of its environment's name it skips the provider's prompts, as workers do, and carries on the conversation it is given to resume."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def start(self, environment: str, agent: str) -> int:
        return self.launched(environment, [agent, "--env", environment, *DETACHED])

    def start_in_worktree(self, environment: str, agent: str, resume: tuple[str, ...]) -> int:
        WorkspaceWorktree.chosen(self.config.root, environment).created()
        return self.launched(environment, [agent, "--env", environment, "--worktree", environment, *DETACHED, "--skip", "--", *resume])

    def launched(self, environment: str, arguments: list[str]) -> int:
        package = Path(__file__).resolve().parents[2]
        log = self.config.home / "runtime" / f"agent-{environment}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        port = self.config.port_file.read_text().strip() if self.config.port_file.is_file() else str(self.config.port)
        environ = {**os.environ, "JOURNAL_ROOT": str(self.config.root), "JOURNAL_PORT": port}
        with log.open("ab") as output:
            started = subprocess.Popen([sys.executable, str(package / "journal.py"), *arguments], cwd=self.config.root, env=environ, stdin=subprocess.DEVNULL, stdout=output, stderr=output, start_new_session=True)
        return started.pid
