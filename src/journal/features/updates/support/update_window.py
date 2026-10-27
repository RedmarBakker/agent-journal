from dataclasses import dataclass

from journal.support.release import Release


@dataclass(frozen=True)
class UpdateWindow:
    """How far one update reaches: from a version at most this many minor versions before its target within one major, its patches counted with its minor."""

    minors: int

    def is_allowed(self, start: str, target: str) -> bool:
        (start_major, start_minor, _), (target_major, target_minor, _) = Release(start).numbers, Release(target).numbers
        return start_major == target_major and 0 <= target_minor - start_minor <= self.minors

    def starts(self, versions: list[str], target: str) -> list[str]:
        return [version for version in versions if Release(target).is_newer(Release(version)) and self.is_allowed(version, target)]
