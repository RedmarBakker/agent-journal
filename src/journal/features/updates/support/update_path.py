import json
from dataclasses import dataclass

from journal.features.updates.support.no_update_path import NoUpdatePath
from journal.support.release import Release


@dataclass(frozen=True)
class UpdatePath:
    """The releases an update installs one after another to reach the newest step of update_steps.json, each the newest step that accepts the version before it."""

    versions: tuple[str, ...]

    @classmethod
    def planned(cls, installed: str, steps_text: str) -> "UpdatePath":
        steps, here, versions = cls.steps(steps_text), Release(installed), []
        while reachable := [step for step, oldest in steps.items() if step.is_newer(here) and not oldest.is_newer(here)]:
            here = max(reachable, key=lambda step: step.numbers)
            versions.append(here.version)
        beyond = sorted((step for step in steps if step.is_newer(here)), key=lambda step: step.numbers)
        if beyond:
            raise NoUpdatePath(f"no step accepts {here.version}: the next step, {beyond[0].version}, accepts {steps[beyond[0]].version} and newer")
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
