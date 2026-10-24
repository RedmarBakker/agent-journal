from typing import ClassVar

from journal.features.shell.support.shell_data import ShellData
from journal.events.data_source import DataSource


class ShellPart(DataSource[ShellData]):
    """The shell feature's part of the feature data."""

    name: ClassVar[str] = "shell"
