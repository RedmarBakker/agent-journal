import json
from dataclasses import dataclass

from journal.features.updates.support.no_update_path import NoUpdatePath
from journal.support.release import Release


@dataclass(frozen=True)
class UpdatePath:
    """The releases an update installs one after another to reach the newest step of update_steps.json up to the version it installs, each the newest step that accepts the version before it."""

    versions: tuple[str, ...]

    @classmethod
    def planned(cls, installed: str, target: str, steps_text: str) -> "UpdatePath":
        steps, current, versions = {step: oldest for step, oldest in cls.steps(steps_text).items() if not step.is_newer(Release(target))}, Release(installed), []
        while reachable := [step for step, oldest in steps.items() if step.is_newer(current) and not oldest.is_newer(current)]:
            current = max(reachable, key=lambda step: step.numbers)
            versions.append(current.version)
        later_steps = sorted((step for step in steps if step.is_newer(current)), key=lambda step: step.numbers)
        if later_steps:
            raise NoUpdatePath(f"no step accepts {current.version}: the next step, {later_steps[0].version}, accepts {steps[later_steps[0]].version} and newer")
        return cls(tuple(versions))

    @staticmethod
    def steps(text: str) -> dict[Release, Release]:
        if not text.strip():
            raise NoUpdatePath("the newest release publishes no update_steps.json")
        try:
            versions = {Release(version).version: Release(entry["oldest"]).version for version, entry in json.loads(text).items() if entry["step"]}
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise NoUpdatePath(f"update_steps.json cannot be read: {error}") from error
        return {Release(step): Release(oldest) for step, oldest in versions.items()}
