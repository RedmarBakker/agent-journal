from journal.support.option import Option


class ChecksOptions:
    REPEAT = Option("checks.repeat_minutes", "Tell a failing check again after", "Minutes a check goes on failing before the agent is told again; 0 tells it once, when it starts failing", 60, unit="minutes")
