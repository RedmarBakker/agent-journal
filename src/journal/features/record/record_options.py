from journal.support.option import Option


class RecordOptions:
    """The options of the record feature."""

    RECORD_LENGTH = Option("record.kept", "Keep the record's last", "Entries of the journal's record kept, newest first: every hook and row changed, and as many of the lines said to the agent apart; past this the oldest go, while messages, tasks and every other row of the project stay", 10000, unit="entries")
