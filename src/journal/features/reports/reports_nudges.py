from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ReportsNudges:
    """The nudges of the reports feature."""

    UPDATE_SUGGESTION = Nudge("reports", "write_an_update", "after major work, check `journal report changes`, then tell the user: `journal report recap \"<one or two sentences>\"`", "", repeat=Timeout.seconds(0))
