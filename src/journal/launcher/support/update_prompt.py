import os
import subprocess

from journal.config import Config
from journal.support.release import Release
from journal.features.updates.support.release_source import ReleaseSource
from journal.features.updates.support.official_install import OfficialInstall
from journal.launcher.screen import Screen
from journal.launcher.support.option import Option
from journal.sync.team_account import TeamAccount
from journal.version import VERSION

# the longest an update before a launch may take: the release downloaded, installed and set up
UPDATE_SECONDS = 600


class UpdatePrompt:
    """At a launch from a terminal, a release newer than the installed one, of the same major version, is offered before the journal starts, on a shared journal only the version the team is pinned to: yes runs journal update, the one route every update takes (the Updater), no starts as it is."""

    def __init__(self, config: Config, screen: Screen, source: ReleaseSource) -> None:
        self.config, self.screen, self.source = config, screen, source

    def newest(self) -> Release | None:
        installed = Release.lookup([VERSION])[0]
        try:
            newer = [r for r in Release.lookup(self.source.tags(Release.major_prefix(installed.major))) if r.upgrades(installed) and TeamAccount(self.config).allows(r)]
        except (OSError, ValueError):
            return None
        return newer[-1] if newer else None

    def installed_newer(self) -> bool:
        newest = self.newest()
        if newest is None:
            return False
        options = [Option(f"Update to {newest.version}, then start"), Option(f"Start with {VERSION} as it is")]
        if self.screen.pick(f"Version {newest.version} is out", [f"This journal runs {VERSION}."], options, 0) != 0:
            return False
        updated = subprocess.run(["sh", str(self.config.home / "src" / "journal.sh"), "update"], cwd=self.config.root, env={**os.environ, "JOURNAL_ROOT": str(self.config.root)}, capture_output=True, text=True, timeout=UPDATE_SECONDS)
        if updated.returncode == 0 or OfficialInstall(self.config).installation(newest.tag).returncode == 0:
            return True
        self.screen.pick("The update did not finish", [(updated.stderr or updated.stdout).strip()[-300:], f"The journal starts with {VERSION}."], [Option("Start")], 0)
        return False
