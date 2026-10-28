from collections import defaultdict


class CoverageGaps:
    """What the run's stories never made the journal do: the nudges of its registry none of them made the journal give, and the settings none of them made it read, each listed by its feature, the part of its key before the first dot."""

    def __init__(self) -> None:
        self.nudges: set[str] = set()
        self.settings: set[str] = set()
        self.nudge_keys: set[str] = set()
        self.read: set[str] = set()

    def known(self, nudges: list[str], settings: list[str]) -> None:
        self.nudges |= set(nudges)
        self.settings |= set(settings)

    def played(self, nudge_keys: set[str], read: set[str]) -> None:
        self.nudge_keys |= nudge_keys
        self.read |= read

    def lines(self) -> list[str]:
        return [
            f"nudges no story made the journal say: {len(self.nudges - self.nudge_keys)} of {len(self.nudges)}",
            *self.feature_groups(self.nudges - self.nudge_keys),
            f"settings no story made the journal read: {len(self.settings - self.read)} of {len(self.settings)}",
            *self.feature_groups(self.settings - self.read),
        ]

    @staticmethod
    def feature_groups(keys: set[str]) -> list[str]:
        features: dict[str, list[str]] = defaultdict(list)
        for key in sorted(keys):
            feature, _, remainder = key.partition(".")
            features[feature].append(remainder)
        return [f"  {feature} ({len(rests)}): {', '.join(rests)}" for feature, rests in sorted(features.items(), key=lambda item: -len(item[1]))]
