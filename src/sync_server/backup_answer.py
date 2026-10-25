from dataclasses import dataclass


@dataclass(frozen=True)
class BackupAnswer:
    """The file name of the backup the server wrote into its data folder's backups."""

    name: str
