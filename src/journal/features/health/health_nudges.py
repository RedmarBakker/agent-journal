from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout

YEAR_SECONDS = 365 * 86400.0


class HealthNudges:
    PANIC_WATCH = Nudge("health", "start_the_panic_watch", "this is the journal's own repository, and a Claude Code cron job ends with its session", "start the panic watch: a CronCreate job every 15 minutes that checks the journal's health, restarts it with journal setup restart when it does not answer, and tells the user in one line", repeat=Timeout.seconds(0), longest_characters=280, longest_reason="it spells out the whole job of the panic watch, so the agent starts it right")
    UNCHECKED_WORK = Nudge("health", "went_through_unchecked", "while the journal was down, {{kinds|cap=120}}: {{commands|cap=200}}", "check them and rerun what ran unrecorded", repeat=Timeout.seconds(YEAR_SECONDS), longest_characters=402, longest_reason="it lists what ran unchecked while the journal was down")
