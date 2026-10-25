from dataclasses import dataclass

from sync_server.leases import SERVER_LAPSE


@dataclass(frozen=True)
class LeaseRequest:
    """The name of the lease a device takes, renews or lets go, and how long it stands unrenewed once taken, the server's own lapse unless it names one."""

    name: str
    lapse_seconds: float = SERVER_LAPSE
