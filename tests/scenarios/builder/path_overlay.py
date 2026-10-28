from dataclasses import dataclass, field

# two stories sharing this share of their distinct steps walk one path: the shared part belongs in a fixture
FAILING_SHARE = 0.8
# from this share on a pair is named in the report, drifting together
WARNING_SHARE = 0.6


@dataclass
class PathOverlay:
    """The paths of a run's scenarios laid over each other, one provider at a time: a story whose every step another story also makes reaches nothing of its own, and two that share most of their distinct steps walk one path; each finding names the stories and where their paths part."""

    paths: dict[str, list[str]] = field(default_factory=dict)

    def add(self, name: str, path: list[str]) -> None:
        self.paths[name] = path

    def failures(self) -> list[str]:
        return [*self.redundant(), *self.pairs_from(FAILING_SHARE)]

    def warnings(self) -> list[str]:
        return [line for line in self.pairs_from(WARNING_SHARE) if line not in self.pairs_from(FAILING_SHARE)]

    def redundant(self) -> list[str]:
        lines = []
        for name, path in self.paths.items():
            others = set().union(*(set(other) for other_name, other in self.paths.items() if other_name != name))
            if path and set(path) <= others:
                covering = [other_name for other_name, other in self.paths.items() if other_name != name and set(path) & set(other)]
                lines.append(f"{name} reaches nothing the other scenarios do not; covered by {', '.join(covering)}")
        return lines

    def pairs_from(self, share: float) -> list[str]:
        names, lines = sorted(self.paths), []
        for index, first in enumerate(names):
            for second in names[index + 1:]:
                shared = self.share(self.paths[first], self.paths[second])
                if shared >= share:
                    lines.append(f"{first} and {second} share {round(shared * 100)}% of their path, the same for their first {self.common_start(self.paths[first], self.paths[second])} steps: move the shared steps into a fixture and start both from it")
        return lines

    @staticmethod
    def share(first: list[str], second: list[str]) -> float:
        union = set(first) | set(second)
        return len(set(first) & set(second)) / len(union) if union else 0.0

    @staticmethod
    def common_start(first: list[str], second: list[str]) -> int:
        return next((index for index, (one, other) in enumerate(zip(first, second)) if one != other), min(len(first), len(second)))
