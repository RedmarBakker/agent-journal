from dataclasses import dataclass
from typing import ClassVar

from journal.events.pool_job_arrived import PoolJobArrived
from journal.models.model import Model
from journal.models.pool_job_state import PoolJobState


@dataclass(frozen=True)
class PoolJob(Model):
    """A worker the team's pool offered this machine: the team server's request number, the environment that asked and the person who asked, the worker's number there and the profile it works by, where it stands and why it was turned down. Kept on this machine."""

    shared: ClassVar[bool] = False
    timeline_visible: ClassVar[bool] = False

    request_id: int = 0
    environment_key: str = ""
    account_id: int = 0
    worker_id: int = 0
    profile: str = ""
    state: PoolJobState = PoolJobState.WAITING
    reason: str = ""

    def arrived(self) -> "PoolJob":
        return self.with_event(PoolJobArrived(request_id=self.request_id))

    def started(self) -> "PoolJob":
        return self.with_(state=PoolJobState.STARTED)

    def declined(self, reason: str) -> "PoolJob":
        return self.with_(state=PoolJobState.DECLINED, reason=reason)

    def finished(self) -> "PoolJob":
        return self.with_(state=PoolJobState.FINISHED)
