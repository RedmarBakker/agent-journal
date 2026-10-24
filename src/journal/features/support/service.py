from dataclasses import dataclass


@dataclass(frozen=True)
class Service:
    """A process a feature needs beside the agent: a module of the package, run with the package's own Python and running by the supervisor that hosts the journal, and the path of the health URL it answers on the loopback port it is given, if it answers one."""

    name: str
    module: str
    health_path: str = ""
