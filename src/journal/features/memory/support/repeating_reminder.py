from dataclasses import dataclass

from journal.support.moment import Moment
from journal.support.timeout import Timeout


@dataclass(frozen=True)
class RepeatingReminder:
    """A reminder with an interval: its number, its words, its interval in minutes or tool uses, and the moment and tool use it was last sent."""

    id: int
    text: str
    every_minutes: int
    every_tool_uses: int
    said_at: float
    said_tool_use: int

    def is_due(self, time: float, tool_use: int) -> bool:
        interval = Timeout.minutes(self.every_minutes) if self.every_minutes else Timeout.tool_uses(self.every_tool_uses)
        return interval.reset(Moment(seconds=self.said_at, tool_uses=self.said_tool_use)).has_passed(Moment(seconds=time, tool_uses=tool_use))
