from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class EngineNudges:
    """The lines the engine says itself, which no feature owns."""

    STOP_LOOP = Nudge("engine", "stop_held_in_a_loop", "stop held five times; the next goes through", "fix the state with `journal panic <state>`, then `journal panic report`", repeat=Timeout.seconds(0))

    JOBLESS_HELPER = Nudge("engine", "helper_has_no_job", "you have no job yet", "wait for the journal to give you one, or run the journal command it gave you", repeat=Timeout.seconds(0))
    GUARD_FAILED = Nudge("engine", "guard_failed", "a guard failed and let this through: {{text|cap=22}}", "the journal recorded it; tell the user if it happens again", repeat=Timeout.seconds(0))

    LOCKOUT_WAIT = Nudge("engine", "journal_answers_again", "your journal was down for {{seconds}} seconds and is back", "tools wait a few seconds until it is steady; try again then", repeat=Timeout.seconds(0))
    LOCKOUT_END = Nudge("engine", "worker_ends_after_the_grace", "your journal was down {{seconds}} seconds, past a worker's {{grace}}-second limit", "stop now; you will be sent again", repeat=Timeout.seconds(0))

    ALL = (STOP_LOOP, GUARD_FAILED, JOBLESS_HELPER, LOCKOUT_WAIT, LOCKOUT_END)
