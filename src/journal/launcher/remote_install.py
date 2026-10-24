import argparse
import shlex
import subprocess
import sys

from journal.version import VERSION

INSTALLER = "https://github.com/jessegall/agent-journal/releases/download/v{version}/install.sh"


class RemoteInstall:
    """Installs the team server, with the team's hosted journal, on a machine reached over SSH with a key it already accepts: the release's installer runs there through ssh -t, so its questions are asked in this terminal and it prints the address and the line to join with. Run in a terminal, never in an agent's shell, which has none."""

    def __init__(self, target: str, version: str) -> None:
        self.target, self.version = target, version

    @classmethod
    def parsed(cls, argv: list[str]) -> "RemoteInstall":
        parser = argparse.ArgumentParser(prog="journal remote install", description="install the team server and its hosted journal on a machine over SSH")
        parser.add_argument("verb", choices=["install"])
        parser.add_argument("target", help="the machine, as ssh names it: user@host")
        parser.add_argument("--version", default=VERSION, help="the release to install; this journal's own by default")
        args = parser.parse_args(argv)
        return cls(args.target, args.version)

    def command(self) -> list[str]:
        settings = "".join(f"{name}={shlex.quote(value)} " for name, value in self.installer_settings().items())
        return ["ssh", "-t", self.target, f"curl -fsSL {INSTALLER.format(version=self.version)} | {settings}sh"]

    def installer_settings(self) -> dict[str, str]:
        host = self.target.rsplit("@", 1)[-1]
        return {"TEAM_ADDRESS": host} if "." in host or ":" in host else {}

    def run(self) -> int:
        if not sys.stdin.isatty():
            print("journal remote install asks its questions in a terminal: run it in yours, not in an agent's shell", file=sys.stderr)
            return 2
        return subprocess.call(self.command())
