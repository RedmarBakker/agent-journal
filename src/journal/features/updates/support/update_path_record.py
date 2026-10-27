from dataclasses import dataclass, replace

from journal.support.release import Release


@dataclass(frozen=True)
class UpdatePathRecord:
    """A path of steps as install.sh records it: the version it started from, the version it ends at, the steps before that, the last step installed, the step that failed, and whether the user closed it after a failure."""

    start: str
    target: str
    steps: tuple[str, ...]
    reached: str
    failed: str
    closed: bool

    @classmethod
    def read(cls, data: dict) -> "UpdatePathRecord":
        return cls(data["from"], data["to"], tuple(data["steps"]), data["reached"], data["failed"], bool(data.get("closed")))

    @classmethod
    def empty(cls) -> "UpdatePathRecord":
        return cls("", "", (), "", "", False)

    def as_data(self) -> dict:
        return {"from": self.start, "to": self.target, "steps": list(self.steps), "reached": self.reached, "failed": self.failed, "closed": self.closed}

    def has_failed(self, version: str) -> bool:
        return self.reached == version and bool(self.failed)

    def is_unfinished(self, version: str) -> bool:
        return not self.failed and self.target != version and version in (self.start, *self.steps)

    def versions(self) -> tuple[str, ...]:
        return (*self.steps, self.target)

    def next_version(self, version: str) -> str:
        return next(later for later in self.versions() if Release(later).is_newer(Release(version)))

    def step_line(self, version: str) -> str:
        versions, upcoming = self.versions(), self.next_version(version)
        return f"Updating from {self.start} to {self.target} in {len(versions)} steps: installing {upcoming}, step {versions.index(upcoming) + 1} of {len(versions)}"

    def problem(self, version: str) -> str:
        if not self.has_failed(version) or self.closed:
            return ""
        return f"The update to {self.target} stopped at {version}: the step to {self.failed} failed, and {version} keeps running. journal update retry tries {self.failed} again; journal update close keeps {version}"

    def closed_record(self) -> "UpdatePathRecord":
        return replace(self, closed=True)
