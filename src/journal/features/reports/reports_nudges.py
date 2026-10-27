from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ReportsNudges:
    """The nudges of the reports feature."""

    UPDATE_SUGGESTION = Nudge("reports", "write_an_update", "you committed work: if a meaningful piece landed, write the user an update", "journal report changes shows what it covers, then journal report recap \"<one or two sentences>\" writes it, docked at the bottom of the chat; skip it when the work is small", repeat=Timeout.seconds(0))
    UNACTED = Nudge("reports", "written_work_never_acted_on", "{{row_type}} {{n}} has not been read, linked or mentioned since it was written", "read it and act on it, linking it to the task or plan it feeds, or sign it off with journal {{kind}} settle {{n}} --why \"<why it needs no action>\"", repeat=Timeout.minutes(30))
