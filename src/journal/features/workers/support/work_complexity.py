from dataclasses import dataclass

from journal.models.model_tier import ModelTier
from journal.models.support.model_fit import RIGHT, TOO_STRONG, TOO_WEAK, ModelFit

# what each recorded measure of a worker's work adds to its complexity, a point each so much
LINES_A_POINT, FILES_A_POINT, TOOL_USES_A_POINT, MINUTES_A_POINT, TESTS_A_POINT = 40, 2, 30, 15, 2
SEND_BACK_POINTS = 2
# a brief that names no files leaves the worker to find them
UNNAMED_FILES_POINTS = 1
# the points under which the fast model is called for, and from which the strongest is
FAST_UNDER, STRONGEST_FROM = 4, 16
# the send-backs after which work on a weaker model than it called for counts as too weak
REPEATED_SEND_BACKS = 2


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
        named = 0 if self.brief_named_files else UNNAMED_FILES_POINTS
        return round(self.lines / LINES_A_POINT + self.files / FILES_A_POINT + SEND_BACK_POINTS * self.send_backs + self.tool_uses / TOOL_USES_A_POINT + self.minutes / MINUTES_A_POINT + self.tests_added / TESTS_A_POINT + named, 1)

    def called_for(self) -> ModelTier:
        points = self.points()
        if points < FAST_UNDER:
            return ModelTier.FAST
        return ModelTier.STRONGEST if points >= STRONGEST_FROM else ModelTier.GENERAL

    def fit(self, tier: ModelTier) -> ModelFit:
        called_for = self.called_for()
        return ModelFit(self.points(), called_for, tier, self.measured(tier, called_for))

    def measured(self, tier: ModelTier, called_for: ModelTier) -> str:
        if tier == ModelTier.UNKNOWN or not self.files:
            return ""
        if tier.rank() > called_for.rank():
            return TOO_STRONG
        return TOO_WEAK if tier.rank() < called_for.rank() and self.send_backs >= REPEATED_SEND_BACKS else RIGHT
