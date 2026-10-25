import json
import subprocess
from pathlib import Path

from journal.features.plugins.support.manifest_reader import MANIFEST
from journal.features.updates.support.release_source import ReleaseSource
from journal.support.release import Release

NEWEST_TAGS = 50
GIT_SECONDS = 120


class PluginTags:
    """The release tags of a plugin's source, a git address or a folder, and what each needs: the tags that name a release, at most the fifty, and the lowest journal version each tag's manifest says it runs on; one reader for the install of a plugin and for the upgrade of every plugin."""

    def __init__(self, source: ReleaseSource) -> None:
        self.source = source

    def releases(self, source: str) -> list[Release]:
        tags = self.folder_tags(Path(source)) if Path(source).is_dir() else self.source.release_tags(source)
        return Release.lookup(tags)

    @staticmethod
    def folder_tags(folder: Path) -> list[str]:
        if subprocess.run(["git", "-C", str(folder), "remote"], capture_output=True, text=True, timeout=GIT_SECONDS).stdout.strip():
            subprocess.run(["git", "-C", str(folder), "fetch", "--tags", "--quiet"], capture_output=True, text=True, timeout=GIT_SECONDS)
        return subprocess.run(["git", "-C", str(folder), "tag"], capture_output=True, text=True, timeout=GIT_SECONDS).stdout.split()

    def listed(self, source: str) -> list[Release]:
        try:
            return self.newest(source)
        except OSError:
            return []

    def newest(self, source: str) -> list[Release]:
        return self.releases(source)[-NEWEST_TAGS:]

    def newer(self, source: str, current: Release) -> list[Release]:
        return [release for release in self.releases(source) if release.is_newer(current)][:NEWEST_TAGS]

    @staticmethod
    def needs(repository: Path, release: Release) -> str:
        shown = subprocess.run(["git", "-C", str(repository), "show", f"{release.tag}:{MANIFEST}"], capture_output=True, text=True, timeout=GIT_SECONDS)
        return str(json.loads(shown.stdout or "{}").get("journal", "")) if shown.returncode == 0 else ""

    def fitting(self, repository: Path, releases: list[Release], journal: Release) -> Release | None:
        return next((release for release in reversed(releases) if not self.needs(repository, release) or not Release(self.needs(repository, release)).is_newer(journal)), None)
