from enum import StrEnum


class EdgeKind(StrEnum):
    """The five kinds of communication edge between two agents, spelled as the contract files spell them."""

    DELEGATES_TO = "delegates_to"
    SPAWNED_BY = "spawned_by"
    ESCALATES_TO = "escalates_to"
    CAN_OBSERVE = "can_observe"
    COLLABORATES_WITH = "collaborates_with"
