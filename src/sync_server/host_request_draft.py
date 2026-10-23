from dataclasses import asdict, dataclass

from sync_server.host_request import HostRequest
from sync_server.request_audience import RequestAudience


@dataclass(frozen=True)
class HostRequestDraft:
    """A request to another machine before the server has numbered it: the environment's key, the kind and what it carries, the account it is asked for and when, who takes it up, the device it is addressed to and the version a pool machine must run."""

    environment_key: str
    kind: str
    body: dict
    account_id: int
    created_at: float
    audience: RequestAudience = RequestAudience.HOST
    device_id: int = 0
    version: str = ""

    def numbered(self, id: int) -> HostRequest:
        return HostRequest(id=id, **asdict(self))
