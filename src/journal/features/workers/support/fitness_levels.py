class FitnessLevels:
    """The multiples of a step a fitness score falls past: the level a score stands on is the next multiple at or above it, and it fell when that is below the level kept last; the level kept after each score is the one it stands on, so a rise lets the levels above be told again."""

    @staticmethod
    def standing(score: int, step: int) -> int:
        return -(-score // step) * step

    @classmethod
    def is_fall(cls, score: int, last_level: int, step: int) -> bool:
        return cls.standing(score, step) < last_level
