from dataclasses import dataclass

from sync_server.leases import LAPSE_SECONDS


@dataclass(frozen=True)
class LeaseRequest:
    """The name of the lease a device takes, renews or lets go, and how long it stands unrenewed once taken."""

    name: str
    lapse_seconds: float = LAPSE_SECONDS
