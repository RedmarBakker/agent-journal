from dataclasses import dataclass
from typing import ClassVar

from journal.models.scoped import Scoped

RECURRING_LIFETIME_SECONDS = 7 * 24 * 3600


@dataclass(frozen=True)
class ScheduledJob(Scoped):
    """A prompt an agent scheduled for itself in its own program, as a Claude Code cron job: the session it lives in, the job's id, its cron schedule, the prompt, whether it repeats, and whether it has ended, cancelled or with its session. A repeating job lapses seven days after it was made. Kept on this machine."""

    shared: ClassVar[bool] = False
    timeline_visible: ClassVar[bool] = False

    session: str = ""
    job_id: str = ""
    cron: str = ""
    prompt: str = ""
    recurring: bool = True
    ended: bool = False

    def ending(self) -> "ScheduledJob":
        return self.with_(ended=True)

    def is_running(self, moment: float) -> bool:
        return not self.ended and (not self.recurring or moment - self.creation_time.timestamp() < RECURRING_LIFETIME_SECONDS)
