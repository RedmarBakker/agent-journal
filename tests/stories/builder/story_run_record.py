import json
from pathlib import Path

from tests.stories.builder.coverage_gaps import CoverageGaps
from tests.stories.builder.path_overlay import PathOverlay

# set by a sharded story run: each shard writes what its stories leave to be checked to this folder
STORY_RECORDS_VARIABLE = "JOURNAL_STORY_RECORDS"


class StoryRunRecord:
    """What a story run leaves to be checked once it has ended: each story's path by provider and mode, each fixture's seeding path by provider, the nudges and settings the stories reached, and the stack changes they walked; written by each shard of a sharded run to a file, merged by the run that started them, and checked the same way as a run in one process."""

    def __init__(self, story_paths: dict[str, dict[str, list[str]]], fixture_paths: dict[str, dict[str, list[str]]], gaps: CoverageGaps, walked: set[str]) -> None:
        self.story_paths, self.fixture_paths, self.gaps, self.walked = story_paths, fixture_paths, gaps, walked

    @classmethod
    def loaded(cls, path: Path) -> "StoryRunRecord":
        data = json.loads(path.read_text())
        gaps = CoverageGaps()
        gaps.known(data["nudges"], data["settings"])
        gaps.played(set(data["nudge_keys"]), set(data["read"]))
        return cls(data["story_paths"], data["fixture_paths"], gaps, set(data["walked"]))

    @classmethod
    def merged(cls, records: list["StoryRunRecord"]) -> "StoryRunRecord":
        story_paths: dict[str, dict[str, list[str]]] = {}
        fixture_paths: dict[str, dict[str, list[str]]] = {}
        gaps, walked = CoverageGaps(), set()
        for record in records:
            for key, paths in record.story_paths.items():
                story_paths.setdefault(key, {}).update(paths)
            for key, paths in record.fixture_paths.items():
                fixture_paths.setdefault(key, {}).update(paths)
            gaps.known(list(record.gaps.nudges), list(record.gaps.settings))
            gaps.played(record.gaps.nudge_keys, record.gaps.read)
            walked |= record.walked
        return cls(story_paths, fixture_paths, gaps, walked)

    def saved(self, path: Path) -> None:
        path.write_text(json.dumps({"story_paths": self.story_paths, "fixture_paths": self.fixture_paths, "nudges": sorted(self.gaps.nudges), "settings": sorted(self.gaps.settings), "nudge_keys": sorted(self.gaps.nudge_keys), "read": sorted(self.gaps.read), "walked": sorted(self.walked)}))

    def failures(self) -> list[str]:
        failures = [f"[{key}] {line}" for key, paths in self.story_paths.items() for line in PathOverlay(paths).failures()]
        for provider, paths in self.fixture_paths.items():
            failures += [f"[fixtures on {provider}] {line}" for line in PathOverlay(paths).failures() if " reaches nothing " not in line]
            failures += [f"[fixtures on {provider}] {name} adds no step to the fixture it starts from" for name, path in paths.items() if len(path) < 2]
        return failures

    def warnings(self) -> list[str]:
        return [f"[{key}] {line}" for key, paths in self.story_paths.items() for line in PathOverlay(paths).warnings()]

    def report_lines(self) -> list[tuple[str, bool]]:
        return [*((line, False) for line in self.gaps.lines()), *((f"story paths, drifting together: {line}", False) for line in self.warnings()), *((f"story paths, failed: {line}", True) for line in self.failures())]
