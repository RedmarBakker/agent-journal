from dataclasses import dataclass, field

# two stories sharing this share of their distinct steps walk one path: the shared part belongs in a fixture
FAILING_SHARE = 0.8
# from this share on a pair is named in the report, drifting together
WARNING_SHARE = 0.6


@dataclass
class PathOverlay:
    """The paths of a run's stories laid over each other, one provider at a time: a story whose every step, and every step taken right after another, another story also makes reaches nothing of its own, so a stop let through after a wait differs from one refused after it, and the same steps from another fixture are a path of their own; and two that share most of their distinct steps walk one path; each finding names the stories and where their paths part."""

    paths: dict[str, list[str]] = field(default_factory=dict)

    def add(self, name: str, path: list[str]) -> None:
        self.paths[name] = path

    def failures(self) -> list[str]:
        return [*self.redundant(), *self.alike_pairs(FAILING_SHARE)]

    def warnings(self) -> list[str]:
        return [line for line in self.alike_pairs(WARNING_SHARE) if line not in self.alike_pairs(FAILING_SHARE)]

    def redundant(self) -> list[str]:
        lines = []
        for name, path in self.paths.items():
            neighbour_elements = set().union(*(self.elements(neighbour) for neighbour_name, neighbour in self.paths.items() if neighbour_name != name))
            if path and self.elements(path) <= neighbour_elements:
                covering = [neighbour_name for neighbour_name, neighbour in self.paths.items() if neighbour_name != name and self.elements(path) & self.elements(neighbour)]
                lines.append(f"{name} reaches nothing the other stories do not; covered by {', '.join(covering)}")
        return lines

    def alike_pairs(self, share: float) -> list[str]:
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
        start = path[0] if path else ""
        return {f"{start}: {step}" for step in path} | {f"{start}: {step} then {following}" for step, following in zip(path, path[1:])}

    @staticmethod
    def common_start(first: list[str], second: list[str]) -> int:
        return next((index for index, (first_step, second_step) in enumerate(zip(first, second)) if first_step != second_step), min(len(first), len(second)))
