from sync_server.backup_answer import BackupAnswer
from sync_server.devices import Devices
from sync_server.server_backups import ServerBackups

MIGRATION_STEM = "team-before-hub"


class BackupHandler:
    """An admin's request, made before the team moves to the hub, that the server write a backup of the team's database, answered with its file name."""

    def __init__(self, devices: Devices, backups: ServerBackups) -> None:
        self.devices, self.backups = devices, backups

    def answer(self, token: str) -> BackupAnswer:
        self.devices.admin(token)
        return BackupAnswer(self.backups.written(MIGRATION_STEM).name)
