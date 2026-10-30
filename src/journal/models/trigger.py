from typing import ClassVar
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from journal.events.rows.trigger_fired import TriggerFired
from journal.models.model import Model
from journal.models.trigger_action import TriggerAction
from journal.support.cron_line import CronLine
from journal.support.phrases import Phrases


@dataclass(frozen=True)
class Trigger(Model):
    """Words the user chose, and what the journal does when one comes up in a prompt or a tool call; or a time, once, every so many minutes or on a cron line, when the journal sends its line, until its end or its number of times."""

    text_fields: ClassVar[tuple[str, ...]] = ("phrases",)
    phrases: tuple[str, ...] = ()
    action: TriggerAction = TriggerAction.NUDGE
    text: str = ""
    is_scheduled: bool = False
    next_at: datetime | None = None
    interval_minutes: int = 0
    cron_line: str | None = None
    end_at: datetime | None = None
    fire_limit: int = 0
    fired_count: int = 0

    def matches(self, text: str) -> bool:
        return any(Phrases.contains(text, phrase) for phrase in self.phrases)

    def summary_line(self) -> str:
        return self.opening_line(self.text)

    def is_finished(self) -> bool:
        return self.is_scheduled and self.next_at is None

    def fired(self, time: float) -> "Trigger":
        count = self.fired_count + 1
        event = TriggerFired(time=time, row_id=self.id, text=self.text, action=self.action)
        return self.with_(fired_count=count, next_at=self.next_time(count)).with_event(event)

    def next_time(self, count: int) -> datetime | None:
        if self.fire_limit and count >= self.fire_limit:
            return None
        following = self.following_time(self.next_at)
        return following if following is not None and (self.end_at is None or following <= self.end_at) else None

    def following_time(self, moment: datetime) -> datetime | None:
        if self.interval_minutes:
            return moment + timedelta(minutes=self.interval_minutes)
        if self.cron_line is not None:
            return CronLine.parsed(self.cron_line).following_time(moment.astimezone().replace(tzinfo=None)).astimezone(timezone.utc)
        return None
