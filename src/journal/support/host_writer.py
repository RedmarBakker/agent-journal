from typing import Callable

from sync_server.host_request import HostRequest


class HostWriter:
    """A feature's writes made here when another journal asks this one, as the host of their environment, to make them: each kind of request it makes, with the method that makes it."""

    def makers(self) -> dict[str, Callable[[HostRequest], None]]:
        return {}
