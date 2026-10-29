from enum import StrEnum


class PlanMode(StrEnum):
    """How a plan is worked: in organization mode its Plan agent coordinates Domain agents and Roles on a rig, in solo mode its Plan agent does the work itself and needs no rig."""

    ORGANIZATION = "organization"
    SOLO = "solo"
