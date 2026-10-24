import os
import socket
import sys
from pathlib import Path

from journal.config import Config
from journal.features.registry import Registry
from journal.features.support.service import Service
from journal.supervisor_link import SupervisorLink
from journal.support.supervisor_reply import SupervisorReply


class ServiceStart:
    """At boot, the journal asks the supervisor that hosts it to start every service the features declare, its module run with the installed package importable and the project's folder as its argument and its working folder, and one that answers a health URL given a free loopback port as its second argument and checked there by the supervisor; one already running is not changed, so a restart starts nothing twice and an upgrade's new service starts with the journal it was installed with."""

    def __init__(self, registry: Registry, link: SupervisorLink, config: Config) -> None:
        self.registry, self.link, self.config = registry, link, config

    def run(self) -> list[SupervisorReply]:
        host = self.link.hosting()
        if host is None:
            self.disabled()
            return []
        return [self.started(host, service) for service in self.registry.services()]

    def started(self, host: int, service: Service) -> SupervisorReply:
        package = Path(__file__).resolve().parents[4]
        environ = {**os.environ, "PYTHONPATH": str(package)}
        command, log = [sys.executable, "-m", service.module, str(self.config.root)], self.config.home / "runtime" / f"{service.name}.log"
        if not service.health_path:
            return self.link.start(host, service.name, command, self.config.root, environ, log, {})
        port = self.free_port()
        return self.link.start(host, service.name, [*command, str(port)], self.config.root, environ, log, {"url": f"http://127.0.0.1:{port}{service.health_path}"})

    @staticmethod
    def free_port() -> int:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            return probe.getsockname()[1]

    def disabled(self) -> None:
        names = [service.name for service in self.registry.services()]
        if names:
            print(f"no supervisor hosts this journal, so these services are off: {', '.join(names)}", flush=True)
