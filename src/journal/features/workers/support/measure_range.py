from dataclasses import dataclass


@dataclass(frozen=True)
class MeasureRange:
    """A measure's range with hysteresis: the value makes it failing past the fail level and passing again only back at the pass level; a fail level at or over the pass level bounds the value from above, one under it from below."""

    fail_level: float
    pass_level: float

    def is_failing(self, failing: bool, value: float) -> bool:
        level = self.pass_level if failing else self.fail_level
        return value > level if self.fail_level >= self.pass_level else value < level
