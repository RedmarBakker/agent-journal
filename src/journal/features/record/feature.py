from journal.features.feature import Feature
from journal.features.record.listeners.fault_cards import FaultCards
from journal.features.record.jobs.record_trim import RecordTrim
from journal.features.record.record_options import RecordOptions


class Record(Feature):
    """The journal's record of what happened: every hook, line sent and row changed, stored as a rolling log, and a session that started without its launch id or a guard that failed marked in the chat."""

    name = "record"
    title = "Record"
    help = "The journal keeps a record of every hook, line said and row changed, as a rolling log of its newest entries, trimmed every five minutes; the project's own rows, messages among them, are never trimmed."
    fixed = True
    options = (RecordOptions.RECORD_LENGTH,)
    listeners = (FaultCards,)
    jobs = (RecordTrim,)
