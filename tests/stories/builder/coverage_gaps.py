from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class CoverageGaps:
    """What the run's stories never made the journal do: the nudges of its registry none of them caused to be said, and the settings none of them caused to be read, each listed by its feature, the part of its key before the first dot."""

    nudges: set[str] = field(default_factory=set)
    settings: set[str] = field(default_factory=set)
    said: set[str] = field(default_factory=set)
    read: set[str] = field(default_factory=set)

    def known(self, nudges: list[str], settings: list[str]) -> None:
        self.nudges |= set(nudges)
        self.settings |= set(settings)

    def played(self, said: set[str], read: set[str]) -> None:
        self.said |= said
        self.read |= read

    def lines(self) -> list[str]:
        return [
            f"nudges no story made the journal say: {len(self.nudges - self.said)} of {len(self.nudges)}",
            *self.by_feature(self.nudges - self.said),
            f"settings no story made the journal read: {len(self.settings - self.read)} of {len(self.settings)}",
            *self.by_feature(self.settings - self.read),
        ]

    @staticmethod
    def by_feature(keys: set[str]) -> list[str]:
        features: dict[str, list[str]] = defaultdict(list)
        for key in sorted(keys):
            feature, _, rest = key.partition(".")
            features[feature].append(rest)
        return [f"  {feature} ({len(rests)}): {', '.join(rests)}" for feature, rests in sorted(features.items(), key=lambda item: -len(item[1]))]
