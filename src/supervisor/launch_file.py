import json
import os
from pathlib import Path

from supervisor.bad_launch_file import BadLaunchFile
from supervisor.band import Band
from supervisor.band_labels import BandLabels
from supervisor.front_health import FrontHealth
from supervisor.health_check import HealthCheck
from supervisor.inbox import Inbox
from supervisor.screen_copy import ScreenCopy
from supervisor.service import Service
from supervisor.services import Services
from supervisor.supervisor import Supervisor
from supervisor.terminal import Terminal

PROCESS = ("command", "folder", "env")


class LaunchFile:
    """What a supervisor starts from, as the journal wrote it: the agent in front and how to tell its hooks went silent, the services beside it each with its health check, where its socket, announce file and mirror go, the band's words, and the process that owns it, whose end ends it."""

    def __init__(self, data: dict, path: Path) -> None:
        self.data, self.path = data, path

    @classmethod
    def read(cls, path: Path) -> "LaunchFile":
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError) as fault:
            raise BadLaunchFile(f"the launch file {path} cannot be read: {fault}") from fault
        missing = [key for key in ("front", "socket", "announce") if key not in data]
        missing += [f"front's {key}" for key in PROCESS if key not in data.get("front", {})]
        missing += [f"{service.get('name', 'a service')}'s {key}" for service in data.get("services", []) for key in ("name", "log", *PROCESS) if key not in service]
        if missing:
            raise BadLaunchFile(f"the launch file {path} has no {', '.join(missing)}")
        return cls(data, path)

    # beside the announce file, one per environment, so a supervisor started again for it finds what the last one left
    def record_path(self) -> Path:
        announce = Path(self.data["announce"])
        return announce.with_name(f"{announce.name}.services")

    def supervisor(self) -> Supervisor:
        front = self.data["front"]
        services = Services(*(Service(s["name"], s["command"], Path(s["folder"]), s["env"], Path(s["log"]), s.get("keep", True), HealthCheck(**s["health"]) if s.get("health") else None) for s in self.data.get("services", [])))
        front_health = FrontHealth(**front["health"]) if front.get("health") else None
        band = Band(BandLabels.parsed(self.data["band"])) if self.data.get("band") and os.isatty(1) else None
        screen_copy = ScreenCopy(Path(self.data["screen"])) if self.data.get("screen") else None
        return Supervisor(Terminal(front["command"], front["folder"], front["env"], tuple(front.get("resume", ()))), Inbox(Path(self.data["socket"]), Path(self.data["announce"])), services, stdin=0 if os.isatty(0) else None, band=band, screen_copy=screen_copy, faults=Path(self.data["announce"]).parents[1] / "supervisor.log", launch=self.path, owner=int(self.data.get("owner", 0)), front_health=front_health, record=self.record_path())
