from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout

YEAR_SECONDS = 365 * 86400.0


class HealthNudges:
    UNCHECKED_WORK = Nudge("health", "went_through_unchecked", "while the journal did not answer, {{kinds}}: {{commands}}", "check them, and run again what ran unrecorded", repeat=Timeout.seconds(YEAR_SECONDS))
