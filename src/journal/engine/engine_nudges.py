from journal.engine.nudge import Nudge


class EngineNudges:
    """The lines the engine says itself, which no feature owns."""

    STOP_LOOP = Nudge("engine", "stop_held_in_a_loop", "your stop was held five times in a row with nothing between, so the journal is probably in a state it cannot leave, and your next stop goes through", "set the state you should be in with `journal panic <state>`, `journal panic pop` or `journal panic idle`, then `journal panic report` files what held you", repeat_interval=0)

    ALL = (STOP_LOOP,)
