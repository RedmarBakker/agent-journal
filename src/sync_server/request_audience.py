from enum import StrEnum


class RequestAudience(StrEnum):
    """Who takes a request up: the host of its environment, any machine of the pool with a free slot, or one machine by its device number."""

    HOST = "host"
    POOL = "pool"
    DEVICE = "device"
