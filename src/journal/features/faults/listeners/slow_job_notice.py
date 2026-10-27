import sys

from journal.events.listener import Listener
from journal.events.slow_tick import SlowTick
from journal.repositories.setting_rows import SettingRows
from journal.engine.support.nudge_log import NudgeLog
from journal.features.faults.faults_nudges import FaultsNudges
from journal.features.faults.faults_options import FaultsOptions


class SlowJobNotice(Listener[SlowTick]):
    """A job's run that took long is written to the journal's log while the developer features are on, and reported to the running agent when the developer setting asks for it."""

    def __init__(self, settings: SettingRows, nudges: NudgeLog) -> None:
        self.settings, self.nudges = settings, nudges

    def handle(self, event: SlowTick) -> None:
        if self.settings.option(FaultsOptions.DEVELOPER):
            sys.stderr.write(f"job {event.job} took {event.seconds:.1f} seconds for one tick\n")
        if self.settings.option(FaultsOptions.JOBS):
            self.nudges.type(FaultsNudges.SLOW_JOB.create(job=event.job, seconds=event.seconds))
