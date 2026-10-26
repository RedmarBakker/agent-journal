from journal.features.workers.support.measure_range import MeasureRange

MINUTES_ZERO_FACTOR = 6
MEAN_ZERO_FACTOR = 3


class Closeness:
    """How close a measure's value comes to its range, from 1 inside it to 0 far off it, one function per kind of value: a share, minutes of a stretch, a mean and a count."""

    @staticmethod
    def share(value: float, range_: MeasureRange) -> float:
        if range_.fail_level >= range_.pass_level:
            return 1.0 if value <= range_.pass_level else max(0.0, (1 - value) / (1 - range_.pass_level))
        return min(1.0, value / range_.pass_level)

    @staticmethod
    def minutes(value: float, range_: MeasureRange) -> float:
        return Closeness.falling(value, range_.pass_level, range_.pass_level * MINUTES_ZERO_FACTOR)

    @staticmethod
    def mean(value: float, range_: MeasureRange) -> float:
        return Closeness.falling(value, range_.pass_level, range_.pass_level * MEAN_ZERO_FACTOR)

    @staticmethod
    def count(value: float, range_: MeasureRange) -> float:
        return 1.0 if value <= range_.pass_level else 1 / (1 + value - range_.pass_level)

    @staticmethod
    def falling(value: float, full: float, zero: float) -> float:
        if value <= full:
            return 1.0
        return max(0.0, (zero - value) / (zero - full))
