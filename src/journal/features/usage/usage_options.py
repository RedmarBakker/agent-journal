from journal.support.option import Option


class UsageOptions:
    CHECK_MINUTES = Option("usage.check_minutes", "Minutes between limit checks", "While the agent's provider refuses its turns on a usage limit, the journal types nothing to it and tries one turn this often to see whether the limit is over", 15, unit="minutes")
