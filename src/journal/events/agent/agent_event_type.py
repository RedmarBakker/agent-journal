from enum import StrEnum


class AgentEventType(StrEnum):
    """The name each agent event is stored under in the entries, which is its class name."""

    SESSION_STARTED = "SessionStarted"
    SESSION_ENDED = "SessionEnded"
    PROMPT_SUBMITTED = "PromptSubmitted"
    TOOL_STARTING = "ToolStarting"
    TOOL_FINISHED = "ToolFinished"
    TOOL_FAILED = "ToolFailed"
    SUBAGENT_STARTED = "SubagentStarted"
    SUBAGENT_ENDED = "SubagentEnded"
    COMPACTING = "Compacting"
    STOP = "Stop"
    TURN_DISPLAYED = "TurnDisplayed"
