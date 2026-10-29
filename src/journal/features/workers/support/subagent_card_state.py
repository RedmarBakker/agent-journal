from typing import TypedDict


class SubagentCardState(TypedDict):
    """What a subagent's card shows as it runs, refreshed into the card's data: the model, the subagent's session, whether it still runs, its state, why it failed, its outcome and whether the card is final."""

    model: str | None
    subagent: str
    active: bool
    state: str
    reason: str
    outcome: str
    final: bool
