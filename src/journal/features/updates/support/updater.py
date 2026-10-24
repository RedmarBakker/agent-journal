import contextvars
import os
import signal
import subprocess
import threading
import time as timing
from typing import Callable

from journal.config import Config
from journal.support.release import Release
from journal.features.updates.support.release_installer import ReleaseInstaller
from journal.features.updates.support.release_source import ReleaseSource
from journal.features.updates.support.update_card import UpdateCard
from journal.features.updates.support.update_data import UpdateData
from journal.features.updates.support.update_target import UpdateTarget
from journal.features.shell.support.restart_queue import RestartQueue
from journal.supervisor_link import SupervisorLink
from journal.sync.hosting import Hosting
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.repositories.setting_rows import SettingRows
from journal.version import VERSION
from journal.sync.sync_client import SyncClient
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink
from journal.features.updates.updates_options import UpdatesOptions

PLUGIN = "code-commandments"
FIRST_CHECK_DELAY_SECONDS = 60


class Updater:
    """The newest release of the installed major version, or the head of the branch the settings name, asked of GitHub as often as the settings say on a thread of its own, on a shared journal only the version the team is pinned to, and its install: on its own when the user has switched that on, when they say so, or on a hosted journal as soon as the team is pinned to another version; a hosted journal with the auto-update on is the team's own and installs each newer release, pinning the team to it; a member's journal asks the team server for its pin before it leads an upgrade, since the hosted journal may have pinned a newer release since the last pull; a hosted journal restarts by ending its process, which the team image starts again."""

    def __init__(self, settings: SettingRows, source: ReleaseSource, installer: ReleaseInstaller, card: UpdateCard, supervisor: SupervisorLink, config: Config, queue: RestartQueue, account: TeamAccount, client: SyncClient, hosting: Hosting, link: TeamServerLink) -> None:
        self.account, self.client, self.hosting, self.link = account, client, hosting, link
        self.settings, self.source, self.installer = settings, source, installer
        self.card, self.supervisor, self.config, self.queue = card, supervisor, config, queue
        self.releases: list[Release] = []
        self.head = ""
        self.problem = ""
        self.team_version_seen = ""
        self._next_check_at = timing.time() + FIRST_CHECK_DELAY_SECONDS
        self._working = threading.Lock()

    def running(self) -> Release:
        return Release(VERSION)

    def branch(self) -> str:
        return str(self.settings.option(UpdatesOptions.BRANCH)).strip()

    def repository(self) -> str:
        return str(self.settings.option(UpdatesOptions.REPOSITORY)).strip()

    def follow(self, branch: str, actor: Actor) -> None:
        self.settings.set(UpdatesOptions.BRANCH.key, branch.strip(), actor)
        self.head = ""

    def installed_commit(self) -> str:
        stored = self.config.home / "src" / "commit"
        return stored.read_text().strip() if stored.is_file() else ""

    def label(self) -> str:
        return f"{self.branch()} at {self.installed_commit()[:7] or 'an unrecorded commit'}" if self.branch() else VERSION

    def newer(self) -> list[Release]:
        return [release for release in self.releases if release.upgrades(self.running()) and (self.leads_team() or self.account.allows(release))]

    def is_published(self) -> bool:
        if self.branch():
            return bool(self.head) and self.head != self.installed_commit()
        return bool(self.newer())

    def target(self) -> UpdateTarget:
        if not self.is_published():
            raise Rejection(f"there is nothing newer than {self.label()} to install")
        if self.branch():
            return UpdateTarget(self.branch(), f"{self.branch()} at {self.head[:7]}")
        newest = self.newer()[-1]
        return UpdateTarget(newest.tag, newest.version)

    def automatic(self) -> bool:
        return (bool(self.settings.option(UpdatesOptions.AUTO)) or self.is_hosted()) and self.is_published()

    def is_hosted(self) -> bool:
        return self.hosting.is_hosted()

    def leads_team(self) -> bool:
        return self.is_hosted() and bool(self.settings.option(UpdatesOptions.AUTO)) and not self.branch()

    def check_interval_seconds(self) -> int:
        return self.settings.integer(UpdatesOptions.CHECK_INTERVAL) * 60

    def latest(self) -> str:
        if self.branch():
            return self.head[:7]
        newer = self.newer()
        return newer[-1].version if newer else VERSION

    def data(self) -> UpdateData:
        blocked = self.card.running()
        return UpdateData(installed=self.label(), latest=self.latest(), newer=self.is_published(), branch=self.branch(), versions=[release.version for release in self.newer()],
                              updating=blocked.target if blocked else "", step=blocked.step if blocked else "", problem=self.problem)

    def tick(self, time: float) -> None:
        self.reconcile(time)
        if self.is_hosted() and self.account.team_version() not in (VERSION, self.team_version_seen):
            self.team_version_seen = self.account.team_version()
            self.separate(self.checked)
        elif time >= self._next_check_at:
            self._next_check_at = time + self.check_interval_seconds()
            self.separate(self.checked)

    def line(self) -> str:
        if self.problem:
            return self.problem
        if self.is_published():
            return f"{self.target().label} is out; {self.label()} is installed. journal update installs it"
        return f"{self.label()} is the newest commit of the branch" if self.branch() else f"{VERSION} is the newest release of version {self.running().major}"

    def reconcile(self, time: float) -> None:
        blocked = self.card.paused()
        if blocked is None or blocked.is_pending(VERSION, os.getpid(), time):
            return
        self.card.clear()
        self.problem = "" if blocked.target == self.label() else f"The update to {blocked.target} did not finish: .journal/runtime/update.log says how it went"

    def update_immediately(self, actor: Actor) -> None:
        self.read()
        self.card.taken(self.label(), self.target().label)
        if not self.separate(lambda: self.install_newest(actor)):
            raise Rejection("an update is under way already")

    def install(self, actor: Actor) -> None:
        self.read()
        self.card.taken(self.label(), self.target().label)
        self.install_newest(actor)
        if self.problem:
            raise Rejection(self.problem)

    def separate(self, work: Callable[[], None]) -> bool:
        if not self._working.acquire(blocking=False):
            return False
        threading.Thread(target=contextvars.copy_context().run, args=(self.released, work), name="updates", daemon=True).start()
        return True

    def released(self, work: Callable[[], None]) -> None:
        try:
            work()
        except Exception as fault:
            self.problem = f"The update failed: {fault}"
            self.card.clear()
            raise
        finally:
            self._working.release()

    def checked(self) -> None:
        self.lead(VERSION)
        self.read()
        if not self.automatic():
            return
        try:
            self.card.claim(self.label(), self.target().label)
        except Rejection as refused:
            self.problem = str(refused)
            return
        self.install_newest(Actor.user(self.account.user_number()))

    def read(self) -> None:
        try:
            if self.branch():
                self.head = self.source.head_commit(self.repository(), self.branch())
            else:
                self.releases = Release.lookup(self.source.tags(Release.major_prefix(self.running().major)))
            self.problem = ""
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            self.problem = f"The releases could not be read from {self.repository()}: {error}"

    def leads_upgrade(self) -> bool:
        return self.account.is_joined() and not self.is_hosted() and not self.has_newer_pin()

    def has_newer_pin(self) -> bool:
        team_pin = self.link.summary(self.account.address()).version
        return any(pinned.is_newer(self.running()) for pinned in Release.lookup([team_pin]))

    def install_newest(self, actor: Actor) -> None:
        target = self.target()
        drained = self.leads_upgrade()
        if drained:
            self.card.step("Sending this journal's changes to the team")
            self.client.prepare_upgrade()
            self.client.stop()
        self.card.step("Installing the new version")
        try:
            self.installer.run(target.ref, self.repository())
        except Rejection as refused:
            self.problem = str(refused)
            self.card.clear()
            if drained:
                self.client.start()
            return
        self.problem = ""
        self.lead(target.label)
        self.card.step("Restarting the journal")
        self.restart()

    def lead(self, version: str) -> None:
        if not self.leads_team() or not self.account.is_joined():
            return
        if not any(Release(version).is_newer(pinned) for pinned in Release.lookup([self.account.team_version()])):
            return
        try:
            self.link.pin_version(version)
        except (OSError, TeamRefusal) as refused:
            self.problem = f"The team could not be pinned to {version}: {refused}"

    def restart(self) -> None:
        if self.is_hosted():
            os.kill(os.getpid(), signal.SIGTERM)
            return
        host = self.supervisor.hosting()
        outputs = self.queue.update_restart(host) if host is not None else []
        if outputs:
            self.card.step(f"Restarting once outputs {', '.join(str(output.id) for output in outputs)} end")
        elif host is not None and self.queue.is_waiting(host):
            self.card.step("Restarting once the pool workers running here end")
