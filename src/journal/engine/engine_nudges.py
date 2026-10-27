from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class EngineNudges:
    """The lines the engine says itself, which no feature owns."""

    STOP_LOOP = Nudge("engine", "stop_held_in_a_loop", "your stop was held five times in a row with nothing between, so the journal is probably in a state it cannot leave, and your next stop goes through", "set the state you should be in with `journal panic <state>`, `journal panic pop` or `journal panic idle`, then `journal panic report` files what held you", repeat=Timeout.seconds(0))

    JOBLESS_HELPER = Nudge("engine", "helper_has_no_job", "you are not at work: the journal gives you your job", "wait for it, or run the journal command it gave you", repeat=Timeout.seconds(0))
    GUARD_FAILED = Nudge("engine", "guard_failed", "a guard failed and let this through: {{text}}", "the journal recorded it; tell the user if it happens again", repeat=Timeout.seconds(0))

    LOCKOUT_WAIT = Nudge("engine", "journal_answers_again", "your journal did not answer for {{seconds}} seconds and answers again; every tool waits until it has answered for a few seconds", "use the tool again in a few seconds", repeat=Timeout.seconds(0))
    LOCKOUT_END = Nudge("engine", "worker_ends_after_the_grace", "your journal did not answer for {{seconds}} seconds, longer than the {{grace}} seconds a worker waits, so your work ends here", "stop now; the agent that sent you sends you again", repeat=Timeout.seconds(0))

    ALL = (STOP_LOOP, GUARD_FAILED, JOBLESS_HELPER, LOCKOUT_WAIT, LOCKOUT_END)
