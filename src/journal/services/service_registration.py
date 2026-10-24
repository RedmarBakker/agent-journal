from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceRegistration:
    """A service beside the journal: its name, the address the journal posts its events to, and the events it wants."""

    name: str
    address: str
    events: tuple[str, ...]

    def wants(self, event: str) -> bool:
        return event in self.events
