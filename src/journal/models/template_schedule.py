from datetime import datetime
from enum import StrEnum


class TemplateSchedule(StrEnum):
    """How often a plan template starts a plan of its own: never, or once in each day, week, month or quarter."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

    def is_due(self, last: datetime, now: datetime) -> bool:
        return self.period(last.astimezone()) != self.period(now.astimezone())

    def period(self, moment: datetime) -> tuple[int, ...]:
        return PERIODS[self](moment)


PERIODS = {
    TemplateSchedule.NONE: lambda moment: (),
    TemplateSchedule.DAILY: lambda moment: (moment.year, moment.month, moment.day),
    TemplateSchedule.WEEKLY: lambda moment: tuple(moment.isocalendar())[:2],
    TemplateSchedule.MONTHLY: lambda moment: (moment.year, moment.month),
    TemplateSchedule.QUARTERLY: lambda moment: (moment.year, (moment.month - 1) // 3),
}
