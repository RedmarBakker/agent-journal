from typing import TypedDict


class SubagentCardState(TypedDict):
    """What a subagent's card shows as it runs, refreshed into the card's data: the model, the subagent's session and whether it still runs."""

    model: str
    subagent: str
    active: bool
