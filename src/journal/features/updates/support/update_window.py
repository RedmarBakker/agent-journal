from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateWindow:
    """How far one update reaches: from a version at most this many minor versions before its target within one major, its patches counted with its minor."""

    minors: int

    def is_allowed(self, start: str, target: str) -> bool:
        (start_major, start_minor), (target_major, target_minor) = self.number(start)[:2], self.number(target)[:2]
        return start_major == target_major and 0 <= target_minor - start_minor <= self.minors

    def starts(self, versions: list[str], target: str) -> list[str]:
        return [version for version in versions if self.number(version) < self.number(target) and self.is_allowed(version, target)]

    @staticmethod
    def number(version: str) -> tuple[int, ...]:
        return tuple(int(part) for part in version.removeprefix("v").split("."))
