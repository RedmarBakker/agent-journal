from dataclasses import dataclass, field

# two stories sharing this share of their distinct steps walk one path: the shared part belongs in a fixture
FAILING_SHARE = 0.8
# from this share on a pair is named in the report, drifting together
WARNING_SHARE = 0.6


@dataclass
class PathOverlay:
    """The paths of a run's stories laid over each other, one provider at a time: a story whose every step, and every step taken right after another, another story also makes reaches nothing of its own, so a stop let through after a wait differs from one refused after it; and two that share most of their distinct steps walk one path; each finding names the stories and where their paths part."""

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
            others = set().union(*(self.elements(other) for other_name, other in self.paths.items() if other_name != name))
            if path and self.elements(path) <= others:
                covering = [other_name for other_name, other in self.paths.items() if other_name != name and self.elements(path) & self.elements(other)]
                lines.append(f"{name} reaches nothing the other stories do not; covered by {', '.join(covering)}")
        return lines

    def pairs_from(self, share: float) -> list[str]:
        names, lines = sorted(self.paths), []
        for index, first in enumerate(names):
            for second in names[index + 1:]:
                shared = self.share(self.paths[first], self.paths[second])
                if shared >= share:
                    lines.append(f"{first} and {second} share {round(shared * 100)}% of their path, the same for their first {self.common_start(self.paths[first], self.paths[second])} steps: move the shared steps into a fixture and start both from it")
        return lines

    @classmethod
    def share(cls, first: list[str], second: list[str]) -> float:
        union = cls.elements(first) | cls.elements(second)
        return len(cls.elements(first) & cls.elements(second)) / len(union) if union else 0.0

    @staticmethod
    def elements(path: list[str]) -> set[str]:
        return set(path) | {f"{step} then {following}" for step, following in zip(path, path[1:])}

    @staticmethod
    def common_start(first: list[str], second: list[str]) -> int:
        return next((index for index, (one, other) in enumerate(zip(first, second)) if one != other), min(len(first), len(second)))
