import json
from dataclasses import dataclass
from pathlib import Path

from journal.features.updates.support.update_window import UpdateWindow
from journal.version import VERSION
from tests.update_matrix_run import PASSED_FILE, STEPS_FILE, WINDOW, pair_kept, passed_pairs, releases, step

PASSED_REASON = "every release of its window updated to it in the release run"
FAILED_REASON = "an update from a release of its window failed in the release run"
SKIPPED_REASON = "the release run was skipped with JOURNAL_SKIP_UPDATE_MATRIX"


@dataclass(frozen=True)
class UpdateRelease:
    """The update matrix's release run of the version the tree is about to become: refused once that version is tagged, and recorded when its shards return, the tree's pairs kept under the version and the version written to update_steps.json as a step or as no step."""

    version: str
    tags: list[str]
    window: UpdateWindow
    passed_file: Path
    steps_file: Path

    @classmethod
    def current(cls) -> "UpdateRelease":
        return cls(VERSION, releases(), WINDOW, PASSED_FILE, STEPS_FILE)

    def is_tagged(self) -> bool:
        return f"v{self.version}" in self.tags

    def passed(self) -> None:
        for start in self.window.starts(self.tags, self.version):
            pair_kept(self.passed_file, start, f"v{self.version}")
        self.written(step(self.window, self.tags, self.version, passed_pairs(self.passed_file), PASSED_REASON))

    def failed(self) -> None:
        self.written({"step": False, "reason": FAILED_REASON})

    def skipped(self) -> None:
        self.written({"step": False, "reason": SKIPPED_REASON})

    def written(self, entry: dict[str, object]) -> None:
        steps = {**(json.loads(self.steps_file.read_text()) if self.steps_file.is_file() else {}), self.version: entry}
        ordered = dict(sorted(steps.items(), key=lambda item: self.window.number(item[0])))
        self.steps_file.write_text(json.dumps(ordered, indent=1) + "\n")
