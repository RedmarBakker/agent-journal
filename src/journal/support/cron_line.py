from dataclasses import dataclass
from datetime import datetime, timedelta

from journal.support.rejection import Rejection

FIELD_RANGES = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))
SEARCH_DAYS = 366 * 5


@dataclass(frozen=True)
class CronLine:
    """A five-field cron line, minute, hour, day of the month, month and day of the week, each *, a number, a range a-b, a list a,b or a step */n, read in local time; a day of the month and a day of the week both set match on either, as cron does."""

    minutes: frozenset[int]
    hours: frozenset[int]
    days: frozenset[int]
    months: frozenset[int]
    weekdays: frozenset[int]
    days_set: bool
    weekdays_set: bool

    @classmethod
    def parsed(cls, line: str) -> "CronLine":
        fields = line.split()
        if len(fields) != len(FIELD_RANGES):
            raise Rejection(f"a cron line has five fields, minute hour day month weekday, such as '0 9 * * 1-5', not {line!r}")
        minutes, hours, days, months, weekdays = (cls.values(text, low, high) for text, (low, high) in zip(fields, FIELD_RANGES))
        return cls(minutes, hours, days, months, frozenset(day % 7 for day in weekdays), fields[2] != "*", fields[4] != "*")

    @classmethod
    def values(cls, text: str, low: int, high: int) -> frozenset[int]:
        return frozenset(value for part in text.split(",") for value in cls.part_values(part, low, high))

    @classmethod
    def part_values(cls, part: str, low: int, high: int) -> range:
        span, _, step = part.partition("/")
        start, _, end = span.partition("-")
        if not (span == "*" or start.isdigit()) or not (not end or end.isdigit()) or not (not step or step.isdigit()):
            raise Rejection(f"a cron field is *, a number, a range a-b, a list a,b or a step */n, not {part!r}")
        first, last = cls.bounds(start, end, step, high) if span != "*" else (low, high)
        if first < low or last > high or first > last:
            raise Rejection(f"a cron field runs from {low} to {high}, not {part!r}")
        return range(first, last + 1, int(step or 1))

    @staticmethod
    def bounds(start: str, end: str, step: str, high: int) -> tuple[int, int]:
        if end:
            return int(start), int(end)
        return int(start), high if step else int(start)

    def following_time(self, moment: datetime) -> datetime:
        candidate = moment.replace(second=0, microsecond=0) + timedelta(minutes=1)
        limit = candidate + timedelta(days=SEARCH_DAYS)
        while candidate < limit:
            if self.is_match(candidate):
                return candidate
            candidate = self.next_candidate(candidate)
        raise Rejection(f"no minute of the next five years matches the cron line {self}")

    def is_match(self, candidate: datetime) -> bool:
        return candidate.month in self.months and self.is_day(candidate) and candidate.hour in self.hours and candidate.minute in self.minutes

    def next_candidate(self, candidate: datetime) -> datetime:
        if candidate.month not in self.months:
            return (candidate.replace(day=1, hour=0, minute=0) + timedelta(days=32)).replace(day=1)
        if not self.is_day(candidate):
            return candidate.replace(hour=0, minute=0) + timedelta(days=1)
        if candidate.hour not in self.hours:
            return candidate.replace(minute=0) + timedelta(hours=1)
        return candidate + timedelta(minutes=1)

    def is_day(self, candidate: datetime) -> bool:
        day_match, weekday_match = candidate.day in self.days, (candidate.weekday() + 1) % 7 in self.weekdays
        if self.days_set and self.weekdays_set:
            return day_match or weekday_match
        return day_match and weekday_match
