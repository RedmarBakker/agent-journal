from journal.support.option import Option


class MemoryOptions:
    STALENESS_LIMIT = Option("memory.stale_after", "Ask about old rules and reminders after", "Days a rule or reminder stands before the agent is asked at a session start whether it still holds", 7, unit="days")
