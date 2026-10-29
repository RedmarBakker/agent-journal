from journal.references import events
# the agent's own states of work, in which a quiet spell is thinking; waiting, asking, idle and ended are not
WORKING_STATES = frozenset({"working", "following_plan", "delegating", "orchestrating_plan"})

# the moves after which the agent's next step is its own to think out: a tool came back, or the user said something
THINKING_MOVES = (events.TOOL_FINISHED, events.PROMPT_SUBMITTED)

# how long the agent at work has been quiet before it counts as thinking, in seconds: the clock ticks every five seconds, so thinking
# shows five to ten seconds into a quiet spell, about seven and a half on average, past three quarters of this project's gaps between a
# tool's answer and the next step (median 3.3 s, 75th percentile 5.1 s, 90th 8.5 s, over 54110 gaps)
THINKING_SILENCE_SECONDS = 5.0


class ThinkingWindow:
    """Whether the agent is thinking: at work in one of its own states, its last move a tool's answer or the user's words, and quiet for THINKING_SILENCE_SECONDS since; the one place this is decided."""

    @staticmethod
    def opens(state: str, last_move: str, silence_seconds: float) -> bool:
        return state in WORKING_STATES and last_move in THINKING_MOVES and silence_seconds >= THINKING_SILENCE_SECONDS
