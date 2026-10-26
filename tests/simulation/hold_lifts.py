from tests.simulation.trace_entry import TraceEntry

REPEATS = 10


class HoldLifts:
    """A refusal the agent follows up must lift: the same actor refused the same way more than ten times in a row is a hold whose remedy never works."""

    def violated(self, trace: list[TraceEntry]) -> str:
        streaks: dict[tuple[str, str], int] = {}
        for entry in trace:
            key = (entry.actor, entry.action)
            streaks[key] = streaks.get(key, 0) + 1 if entry.refused else 0
            if streaks[key] > REPEATS:
                return f"{entry.actor}'s {entry.action} was refused {streaks[key]} times in a row, by second {entry.second}: a hold that never lifts"
        return ""
