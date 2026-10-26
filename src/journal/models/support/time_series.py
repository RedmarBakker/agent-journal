SHA_COUNT = 50


class TimeSeries:
    """A series of (time in seconds, count) pairs kept on a row: a new pair added with the pairs older than a cutoff dropped, and the total or the number of pairs in the window of some seconds ending at a moment."""

    @staticmethod
    def add(pairs: tuple[tuple[float, int], ...], pair: tuple[float, int], cutoff: float) -> tuple[tuple[float, int], ...]:
        return tuple(entry for entry in (*pairs, pair) if entry[0] >= cutoff)

    @staticmethod
    def total(pairs: tuple[tuple[float, int], ...], moment: float, seconds: float) -> int:
        return sum(count for time, count in pairs if moment - seconds < time <= moment)

    @staticmethod
    def count(pairs: tuple[tuple[float, int], ...], moment: float, seconds: float) -> int:
        return sum(1 for time, _ in pairs if moment - seconds < time <= moment)
