from journal.support.option import Option


class ChecksOptions:
    REPEAT = Option("checks.repeat_minutes", "Tell a failing check again after", "Minutes a check goes on failing before the agent is informed again; 0 informs it once, when it starts failing", 60, unit="minutes")
