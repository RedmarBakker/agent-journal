import subprocess

from journal.config import Config
from journal.support.rejection import Rejection

CLI_SECONDS = 60


class AgentCli:
    """The one way the journal runs the agent program's own command line from the server: with no terminal to read or take over, in a session of its own, so a program that asks something or changes the terminal can never reach the journal's or the agent's, and a program that is missing or slow is a refusal and never a fault."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def run(self, command: list[str]) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(command, cwd=self.config.root, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=CLI_SECONDS, start_new_session=True)
        except (OSError, subprocess.TimeoutExpired) as failed:
            raise Rejection(f"{command[0]} could not be run: {failed}") from failed
