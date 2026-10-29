from dataclasses import dataclass

from journal.models.model_tier import ModelTier
from journal.models.support.model_fit import RIGHT, OVERPOWERED, UNDERPOWERED, ModelFit

# what each recorded measure of a worker's work adds to its complexity, a point each so much
POINT_LINES, POINT_FILES, POINT_TOOL_USES, POINT_MINUTES, POINT_TESTS = 40, 2, 30, 15, 2
REJECTION_POINTS = 2
# a brief that names no files leaves the worker to find them
MISSING_FILE_POINTS = 1
# the points under which the fast model is called for, and from which the strongest is
FAST_UNDER, STRONGEST_FROM = 4, 16
# the send-backs after which work on a weaker model than it called for counts as too weak
REPEATED_REJECTION_COUNT = 2


@dataclass(frozen=True)
class WorkComplexity:
    """How complex a worker's merged work was, from what is recorded of it: the lines and files it changed, the times it was sent back, its tool uses, its minutes, the tests it added and whether its brief named its files; scored in points, which call for the fast model under a few, the strongest from many and the general one between. Set against the model it ran on, work on a stronger model than it called for was too strong, and work sent back again and again on a weaker one too weak; work with no edit recorded is not judged."""

    lines: int
    files: int
    send_backs: int
    tool_uses: int
    minutes: float
    tests_added: int
    brief_named_files: bool

    def points(self) -> float:
        missing_file_points = 0 if self.brief_named_files else MISSING_FILE_POINTS
        return round(self.lines / POINT_LINES + self.files / POINT_FILES + REJECTION_POINTS * self.send_backs + self.tool_uses / POINT_TOOL_USES + self.minutes / POINT_MINUTES + self.tests_added / POINT_TESTS + missing_file_points, 1)

    def fitting_tier(self) -> ModelTier:
        points = self.points()
        if points < FAST_UNDER:
            return ModelTier.FAST
        return ModelTier.STRONGEST if points >= STRONGEST_FROM else ModelTier.GENERAL

    def fit(self, tier: ModelTier) -> ModelFit:
        needed_tier = self.fitting_tier()
        return ModelFit(self.points(), needed_tier, tier, self.measured(tier, needed_tier))

    def measured(self, tier: ModelTier, needed_tier: ModelTier) -> str:
        if tier == ModelTier.UNKNOWN or not self.files:
            return ""
        if tier.rank() > needed_tier.rank():
            return OVERPOWERED
        return UNDERPOWERED if tier.rank() < needed_tier.rank() and self.send_backs >= REPEATED_REJECTION_COUNT else RIGHT
