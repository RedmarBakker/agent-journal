from enum import StrEnum

from journal.support.rejection import Rejection


class PlanMode(StrEnum):
    """How a plan is worked: in organization mode its Plan agent coordinates Domain agents and Roles on a rig, in solo mode its Plan agent does the work itself and needs no rig."""

    ORGANIZATION = "organization"
    SOLO = "solo"

    @classmethod
    def named(cls, name: str) -> "PlanMode":
        if name not in cls._value2member_map_:
            raise Rejection(f"a plan's mode is {' or '.join(cls)}, not {name or 'nothing'}")
        return cls(name)
