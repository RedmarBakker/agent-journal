import re

from journal.models.mcp_server import McpServer
from journal.features.mcp.support.agent_cli import AgentCli
from journal.providers.providers import Providers
from journal.support.rejection import Rejection
from journal.support.cached_answer import CachedAnswer
from journal.features.mcp.support.health_report import HealthReport
from journal.features.mcp.support.server_catalogue import ServerCatalogue

LINE = re.compile(r"^(?P<name>.+?): (?P<how>.+?) - (?P<mark>[✔✘!]) (?P<words>.*)$")
STATES = {"✔": "connected", "✘": "failed", "!": "needs_auth"}
HEALTH_VALIDITY_SECONDS = 3600.0


class Health:
    """The status of each server, as Claude Code's own check reports it: every server the program has, the journal's and the ones set up elsewhere alike."""

    def __init__(self, cli: AgentCli, providers: Providers) -> None:
        self.cli, self.providers = cli, providers
        self._report = CachedAnswer(lambda: self.probe(), HEALTH_VALIDITY_SECONDS, HealthReport())

    def report(self) -> HealthReport:
        return self._report.time()

    def is_recent(self) -> HealthReport:
        return self._report.is_recent()

    def is_checking(self) -> bool:
        return self._report.is_asking()

    def recheck(self) -> None:
        self._report.discard()
        self._report.time()

    @property
    def check_time(self) -> float:
        return self._report.asked_on

    def remove(self, name: str, provider: str) -> bool:
        for command in self.providers.lookup(provider).mcp_remove_commands(name):
            if self.cli.run(command).returncode == 0:
                self.recheck()
                return True
        return False

    def add(self, server: McpServer, provider: str) -> None:
        run = self.cli.run(self.providers.lookup(provider).mcp_add_command(server))
        if run.returncode != 0:
            raise Rejection(f"{provider} did not add {name}: {(run.stderr or run.stdout).strip()[-300:]}")
        self.recheck()

    def probe(self) -> HealthReport:
        try:
            output = self.cli.run(["claude", "mcp", "list"]).stdout
        except Rejection as failed:
            return HealthReport(failure=str(failed))
        rows = {}
        for line in output.splitlines():
            if match := LINE.match(line.strip()):
                rows[match["name"]] = ServerCatalogue(match["name"], match["how"].replace(" (HTTP)", "").replace(" (SSE)", ""), STATES[match["mark"]], match["words"].strip())
        return HealthReport(rows)
