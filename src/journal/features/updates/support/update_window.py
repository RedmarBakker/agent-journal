from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateWindow:
    """How far one update reaches: from a version at most this many minor versions before its target within one major, its patches counted with its minor."""

    minors: int

    def holds(self, start: str, target: str) -> bool:
        (start_major, start_minor), (target_major, target_minor) = self.place(start), self.place(target)
        return start_major == target_major and 0 <= target_minor - start_minor <= self.minors

    @staticmethod
    def place(version: str) -> tuple[int, int]:
        major, minor = version.removeprefix("v").split(".")[:2]
        return int(major), int(minor)
