from argparse import Namespace

from journal.console.command import Command
from journal.features.workers.support.work_mode_briefs import WorkModeBriefs
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows
from journal.support.caller import Caller


class ModeCommand(Command):
    """journal mode show: the work mode in force and what it asks of the agent."""

    noun = "mode"

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def arguments(self, verbs) -> None:
        self.verb(verbs, "show", "print the work mode in force and its brief")

    def show(self, args: Namespace, caller: Caller) -> int:
        mode = str(self.settings.option(WorkersOptions.MODE))
        print(f"you are the {mode}: {WorkModeBriefs.brief(mode)}")
        return 0
