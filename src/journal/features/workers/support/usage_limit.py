import re
from datetime import datetime, timedelta

# the provider's line when a run hits its usage limit, as Claude Code prints it: You've hit your session limit · resets 8:10am
LIMIT_LINE = re.compile(r"hit your (?:session |usage |weekly )?limit.*?resets?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", re.IGNORECASE | re.DOTALL)


class UsageLimit:
    """When a run that stopped at the provider's usage limit may go on: the reset time its last words name, the next such moment from now on this machine's clock, or 0 when they name no limit."""

    @staticmethod
    def reset_at(text: str, now: float) -> float:
        found = LIMIT_LINE.search(text)
        if found is None:
            return 0.0
        hour, minute, half = int(found.group(1)), int(found.group(2) or 0), (found.group(3) or "").lower()
        hour = hour % 12 + (12 if half == "pm" else 0) if half else hour
        if hour > 23 or minute > 59:
            return 0.0
        start = datetime.fromtimestamp(now).astimezone()
        reset = start.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return (reset if reset > start else reset + timedelta(days=1)).timestamp()
