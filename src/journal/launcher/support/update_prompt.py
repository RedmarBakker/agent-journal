import os
import re
import subprocess
import time

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
# how often the installed version is read while a running journal installs the update
INSTALL_POLL_SECONDS = 1.0
INSTALLED_VERSION = re.compile(r'^VERSION = "([^"]+)"', re.MULTILINE)


class UpdatePrompt:
    """At a launch from a terminal, a release newer than the installed one, of the same major version, is offered before the journal starts, on a shared journal only the version the team is pinned to: yes runs journal update, the one route every update takes (the Updater), and waits until the new version is installed, since a running journal installs it after the command returns; no starts as it is."""

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
        if (updated.returncode == 0 and self.installed(newest)) or OfficialInstall(self.config).installation(newest.tag).returncode == 0:
            return True
        self.screen.pick("The update did not finish", [(updated.stderr or updated.stdout).strip()[-300:], f"The journal starts with {VERSION}."], [Option("Start")], 0)
        return False

    def installed(self, newest: Release) -> bool:
        began = time.monotonic()
        frame = 0
        while self.installed_version() != newest.version:
            if time.monotonic() - began > UPDATE_SECONDS:
                return False
            self.screen.progress(frame, f"Installing {newest.version}: the journal starts once it is in")
            frame += 1
            time.sleep(INSTALL_POLL_SECONDS)
        return True

    def installed_version(self) -> str:
        try:
            version_line = INSTALLED_VERSION.search((self.config.home / "src" / "journal" / "version.py").read_text())
        except OSError:
            return ""
        return version_line.group(1) if version_line else ""
