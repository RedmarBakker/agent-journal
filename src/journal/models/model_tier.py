from enum import StrEnum


class ModelTier(StrEnum):
    """How strong a model is among its program's: the fast one, the general one or the strongest; unknown for one the program does not rank."""

    UNKNOWN = ""
    FAST = "fast"
    GENERAL = "general"
    STRONGEST = "strongest"

    def rank(self) -> int:
        return (ModelTier.FAST, ModelTier.GENERAL, ModelTier.STRONGEST).index(self) if self != ModelTier.UNKNOWN else -1
