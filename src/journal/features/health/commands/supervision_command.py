import json
from argparse import Namespace

from journal.console.command import Command
from journal.features.health.health_options import HealthOptions
from journal.repositories.setting_rows import SettingRows
from journal.support.caller import Caller


class SupervisionCommand(Command):
    """journal supervision health: the numbers the supervisor checks the journal's health by, as the launch hands them to it."""

    noun = "supervision"
    default_verb = "health"

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def arguments(self, verbs) -> None:
        self.verb(verbs, "health", "print, as JSON, how often the supervisor checks the journal, how long an answer may take, the misses before a restart and how long a boot is left alone")

    def health(self, args: Namespace, caller: Caller) -> int:
        print(json.dumps({"interval_seconds": self.settings.decimal(HealthOptions.CHECK_SECONDS), "timeout_seconds": self.settings.decimal(HealthOptions.ANSWER_SECONDS),
                          "failures": self.settings.integer(HealthOptions.MISSES), "grace_seconds": self.settings.decimal(HealthOptions.BOOT_SECONDS)}))
        return 0
