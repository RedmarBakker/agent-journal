from datetime import datetime, timedelta
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

    def next_start(self, last: datetime, now: datetime) -> datetime:
        if self.is_due(last, now):
            return now.astimezone()
        local = last.astimezone()
        start = local.replace(hour=0, minute=0, second=0, microsecond=0)
        if self == TemplateSchedule.DAILY:
            return start + timedelta(days=1)
        if self == TemplateSchedule.WEEKLY:
            return start + timedelta(days=7 - local.weekday())
        if self == TemplateSchedule.MONTHLY:
            if local.month == 12:
                return start.replace(year=local.year + 1, month=1, day=1)
            return start.replace(month=local.month + 1, day=1)
        if self == TemplateSchedule.QUARTERLY:
            month = ((local.month - 1) // 3 + 1) * 3 + 1
            if month > 12:
                return start.replace(year=local.year + 1, month=1, day=1)
            return start.replace(month=month, day=1)
        raise ValueError("an unscheduled template has no next start")

    def period(self, moment: datetime) -> tuple[int, ...]:
        return PERIODS[self](moment)


PERIODS = {
    TemplateSchedule.NONE: lambda moment: (),
    TemplateSchedule.DAILY: lambda moment: (moment.year, moment.month, moment.day),
    TemplateSchedule.WEEKLY: lambda moment: tuple(moment.isocalendar())[:2],
    TemplateSchedule.MONTHLY: lambda moment: (moment.year, moment.month),
    TemplateSchedule.QUARTERLY: lambda moment: (moment.year, (moment.month - 1) // 3),
}
