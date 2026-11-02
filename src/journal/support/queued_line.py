import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class QueuedLine:
    """A line to type to an agent, queued while an earlier one is still on its way or while the agent works: the seconds it was to wait go with it, and when it was queued. A remark is never typed: it waits for the agent's next hook."""

    environment_id: int
    line: str
    delay_seconds: float = 0.0
    line_at: float = field(default_factory=time.time)
    is_remark: bool = False
    agent_id: int = 0

    def is_for(self, environment_id: int, agent_id: int = 0) -> bool:
        return self.environment_id == environment_id and (not agent_id or self.agent_id in (0, agent_id))
