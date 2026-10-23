from dataclasses import dataclass

from sync_server.host_request import HostRequest


@dataclass(frozen=True)
class HostRequestList:
    """Host requests as the team server answers them."""

    requests: tuple[HostRequest, ...]
