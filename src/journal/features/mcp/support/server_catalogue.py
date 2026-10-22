from dataclasses import dataclass


@dataclass(frozen=True)
class ServerCatalogue:
    """A server as the agent program's own check reports it: by name, how it is reached, its status and its status text."""

    name: str
    instructions: str
    state: str
    text: str

    @property
    def error(self) -> str:
        return self.text if self.state == "failed" else ""
