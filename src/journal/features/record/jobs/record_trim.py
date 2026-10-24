from journal.engine.job import Job
from journal.features.record.record_options import RecordOptions
from journal.repositories.entries import Entries
from journal.repositories.setting_rows import SettingRows


class RecordTrim(Job):
    """Every five minutes the record is trimmed to its newest entries, as many as the setting allows, in place of a delete at every write; the lines sent to the agents are trimmed separately, to as many of their own newest, since whether a line was sent again is read from them and a flood of row changes must not make the journal forget it sent one; the file returns the space by itself."""

    interval_seconds = 300.0

    def __init__(self, entries: Entries, settings: SettingRows) -> None:
        self.entries, self.settings = entries, settings

    def tick(self, time: float) -> None:
        stored = self.settings.integer(RecordOptions.RECORD_LENGTH)
        self.entries.trim(self.entries.last_id(), stored)
        self.entries.trim_lines(stored)
