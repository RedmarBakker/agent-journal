import contextvars
import os
import signal
import subprocess
import threading
import time as timing
from typing import Callable

from journal.config import Config
from journal.support.release import Release
from journal.features.updates.support.commit_ancestry import CommitAncestry
from journal.features.updates.support.release_installer import ReleaseInstaller
from journal.features.updates.support.official_install import OfficialInstall
from journal.sync.sync_status import SyncStatus
from journal.features.updates.support.release_refusal import ReleaseRefusal
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
from journal.services.service_event import UPGRADE_ABANDONED, UPGRADE_PREPARING, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink
from journal.features.updates.updates_options import UpdatesOptions
from journal.support.time_source import TimeSource

PLUGIN = "code-commandments"
# the longest the sync service may take to send this journal's changes and pull the team's before an install
DRAIN_SECONDS = 60
# what the install command from the README installs when it is asked for no release of its own, and how the card names it
README_REF = "main"
README_TARGET = "the latest release"
# the sync state of a team that does not take this journal's changes now, so an update keeps them here instead of waiting to send them
UNREACHABLE = "not_connected"


class Updater:
    """The newest release of the installed major version, or the head of the branch the settings name, asked of GitHub as often as the settings say on a thread of its own, on a shared journal only the version the team is pinned to, and its install: on its own when the user has switched that on, when they say so, or on a hosted journal as soon as the team is pinned to another version; a hosted journal with the auto-update on is the team's own and installs each newer release, pinning the team to it; a member's journal asks the team server for its pin before it leads an upgrade, since the hosted journal may have pinned a newer release since the last pull; a hosted journal restarts by ending its process, which the team image starts again. The sync service has drained when it has sent the whole queue and pulled the team to its head, under the team's upgrade lease; a journal is pinned when it has joined a team and is not the hosted journal that leads the team onto a release."""

    def __init__(self, settings: SettingRows, source: ReleaseSource, installer: ReleaseInstaller, card: UpdateCard, supervisor: SupervisorLink, config: Config, queue: RestartQueue, account: TeamAccount, hosting: Hosting, link: TeamServerLink, hooks: ServiceHooks, ancestry: CommitAncestry, official: OfficialInstall, sync: SyncStatus, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.official, self.sync = official, sync
        self.ancestry = ancestry
        self.account, self.hosting, self.link, self.hooks = account, hosting, link, hooks
        self.settings, self.source, self.installer = settings, source, installer
        self.card, self.supervisor, self.config, self.queue = card, supervisor, config, queue
        self.releases: list[Release] = []
        self.head = ""
        self.is_head_ahead = False
        self.problem = ""
        self.team_version_seen = ""
        self._next_check_at = self.source.next_check_time(self.check_interval_seconds())
        self.releases = Release.lookup(self.source.stored_tags(Release.major_prefix(self.running().major)))
        self._working = threading.Lock()
        self.started_at = self.time_source.seconds()

    def running(self) -> Release:
        return Release(VERSION)

    def branch(self) -> str:
        return str(self.settings.option(UpdatesOptions.BRANCH)).strip()

    def repository(self) -> str:
        return str(self.settings.option(UpdatesOptions.REPOSITORY)).strip()

    def follow(self, branch: str, actor: Actor) -> None:
        self.settings.set(UpdatesOptions.BRANCH.key, branch.strip(), actor)
        self.head = ""
        self.is_head_ahead = False

    def installed_commit(self) -> str:
        stored = self.config.home / "src" / "commit"
        return stored.read_text().strip() if stored.is_file() else ""

    def label(self) -> str:
        return f"{self.branch()} at {self.installed_commit()[:7] or 'an unrecorded commit'}" if self.branch() else VERSION

    def newer(self) -> list[Release]:
        return [release for release in self.releases if release.upgrades(self.running()) and (self.leads_team() or self.account.allows(release))]

    def is_published(self) -> bool:
        if self.branch():
            return bool(self.head) and self.is_head_ahead
        return bool(self.newer())

    def target(self) -> UpdateTarget:
        if not self.is_published() and self.is_pinned():
            raise Rejection(f"this journal is in a team, and the team decides its version: it pins {self.account.team_version() or 'none yet'}, and this journal runs {self.label()}; the team's admin moves the pin with journal team upgrade")
        if not self.is_published():
            raise Rejection(f"there is nothing newer than {self.label()} to install")
        if self.branch():
            return UpdateTarget(self.branch(), f"{self.branch()} at {self.head[:7]}", f"{self.head[:12]} is ahead of the installed {self.installed_commit()[:12] or 'unrecorded commit'}")
        newest = self.newer()[-1]
        return UpdateTarget(newest.tag, newest.version)

    def automatic(self) -> bool:
        return (bool(self.settings.option(UpdatesOptions.AUTO)) or self.is_hosted() or self.is_pinned()) and self.is_published()

    def is_pinned(self) -> bool:
        return self.account.is_joined() and not self.leads_team()

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
                              updating=blocked.target if blocked else "", step=blocked.step if blocked else "", problem=self.problem, started_at=self.started_at)

    def tick(self, time: float) -> None:
        self.reconcile(time)
        if (self.is_hosted() or self.is_pinned()) and self.account.team_version() not in (VERSION, self.team_version_seen, ""):
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
        self.card.begin(self.label(), self.target().label)
        if not self.separate(lambda: self.install_newest(actor)):
            raise Rejection("an update is under way already")

    def force_update(self) -> None:
        self.card.begin(self.label(), README_TARGET)
        if not self.separate(self.readme_install):
            raise Rejection("an update is under way already")

    def readme_install(self) -> None:
        self.card.step("Running the install command from the README")
        installed = self.official.installation(README_REF)
        if installed.returncode != 0:
            self.problem = f"The install command from the README failed: {(installed.stderr or installed.stdout).strip()[-300:]}"
            self.card.clear()

    def install(self, actor: Actor) -> None:
        self.read()
        self.card.begin(self.label(), self.target().label)
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
                self.is_head_ahead = self.head != self.installed_commit() and self.ancestry.is_newer(self.head, self.installed_commit(), self.repository(), self.branch())
            else:
                self.releases = Release.lookup(self.source.tags(Release.major_prefix(self.running().major)))
            self.problem = ""
        except ReleaseRefusal as refused:
            self._next_check_at = refused.reset_at
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            self.problem = f"The releases could not be read from {self.repository()}: {error}"

    def leads_upgrade(self) -> bool:
        return self.account.is_joined() and not self.is_hosted() and self.sync.state() != UNREACHABLE and not self.has_newer_pin()

    def has_newer_pin(self) -> bool:
        return any(pinned.is_newer(self.running()) for pinned in self.team_pin())

    def team_pin(self) -> list[Release]:
        return Release.lookup([self.link.summary(self.account.address()).version])

    def install_newest(self, actor: Actor) -> None:
        target = self.target()
        drained = self.leads_upgrade()
        if drained:
            self.card.step("Sending this journal's changes to the team")
            if not self.is_drained():
                self.problem = "The sync service did not send this journal's changes to the team, so the new version was not installed"
                self.card.clear()
                self.hooks.post(ServiceEvent(UPGRADE_ABANDONED))
                return
        self.card.step("Installing the new version")
        try:
            self.installer.run(target.ref, self.repository(), target.reason or f"updating to {target.label}")
        except Exception as broken:
            self.installed_officially(target, drained, broken)
            return
        self.recorded(target)
        self.card.step("The new version's install script installs it and restarts the journal on it")
        if self.is_hosted():
            self.restart()

    def installed_officially(self, target: UpdateTarget, drained: bool, broken: Exception) -> None:
        fallback = self.official.installation(target.ref)
        if fallback.returncode != 0:
            self.refused_install(target, drained, f"the update could not install ({broken}), nor could the official install command: {(fallback.stderr or fallback.stdout).strip()[-300:]}")
            return
        self.recorded(target)
        self.card.step("Restarting the journal")
        self.restart()

    def recorded(self, target: UpdateTarget) -> None:
        self.log_reason(target)
        self.problem = ""
        self.lead(target.label)

    def refused_install(self, target: UpdateTarget, drained: bool, reason: str) -> None:
        self.log_reason(target)
        self.problem = reason
        self.card.clear()
        if drained:
            self.hooks.post(ServiceEvent(UPGRADE_ABANDONED))

    def log_reason(self, target: UpdateTarget) -> None:
        if target.reason:
            log = self.config.home / "runtime" / "update.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a") as log_file:
                log_file.write(f"installing {target.label}: {target.reason}\n")

    def is_drained(self) -> bool:
        return self.hooks.succeeded(ServiceEvent(UPGRADE_PREPARING), DRAIN_SECONDS)

    def lead(self, version: str) -> None:
        if not self.leads_team() or not self.account.is_joined():
            return
        try:
            if any(not Release(version).is_newer(pinned) for pinned in self.team_pin()):
                return
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
