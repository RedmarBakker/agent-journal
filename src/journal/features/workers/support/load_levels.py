class LoadLevels:
    """The marks the load is told at, the first level and each step above it: the level a load stands on is the highest mark at or under it, none under the first, and it rose when that is above the level kept for the load before."""

    @staticmethod
    def standing(rho: float, start: float, step: float) -> float:
        return round(start + int((rho - start) / step + 1e-9) * step, 2) if rho >= start else 0.0
