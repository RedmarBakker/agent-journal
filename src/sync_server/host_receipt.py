from dataclasses import dataclass


@dataclass(frozen=True)
class HostReceipt:
    """A host's word that it has made the write asked of it, by the request's number."""

    id: int
