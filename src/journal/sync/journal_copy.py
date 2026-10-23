from journal.db.schema import Schema
from journal.models.outgoing_change import DELETED, OutgoingChange
from journal.models.setting import Setting
from journal.repositories.shared_tables import SharedTables
from journal.sync.setting_scopes import SettingScopes
from journal.support.actor import Actor
from sync_server.copied_row import CopiedRow


class JournalCopy:
    """This journal's shared rows as the team server takes them in a full copy, each row's stored values with every field stamped with the row's update time and the highest number each shared table holds; and the team's full copy taken in place of them: whole when a journal first joins, whose numbers mean nothing to the team, and at an upgrade of the same team the rows kept on this machine alone untouched, the fields a row keeps on this machine alone, as an environment's name, kept on the rows it still holds, and this machine's waiting writes laid on top, so what it has not sent yet still shows here. A setting of one machine or one person is never in the copy either way: this machine's own are kept through it."""

    def __init__(self, tables: SharedTables, scopes: SettingScopes) -> None:
        self.tables, self.scopes = tables, scopes

    def rows(self) -> list[CopiedRow]:
        return [CopiedRow(table, row.row_id, Schema.team_values(row, None), {name: row.updated_at.timestamp() for name in Schema.team_values(row, None)}) for table in self.tables.names() for row in self.tables.rows(table).rows() if self.scopes.is_team_row(row)]

    def highest(self, rows: list[CopiedRow]) -> dict:
        return {table: max((row.row for row in rows if row.row_table == table), default=0) for table in self.tables.names()}

    def replace(self, rows: tuple[CopiedRow, ...], waiting: list[OutgoingChange]) -> None:
        self.rebuilt(rows, self.local_values())
        for change in waiting:
            if self.tables.has(change.row_table):
                self.laid(change)

    def replace_whole(self, rows: tuple[CopiedRow, ...]) -> None:
        self.rebuilt(rows, {})

    def rebuilt(self, rows: tuple[CopiedRow, ...], local: dict[tuple[str, int], dict]) -> None:
        machine_settings = self.machine_settings()
        for table in self.tables.names():
            self.tables.rows(table).clear()
        for row in rows:
            if self.tables.has(row.row_table):
                self.tables.rows(row.row_table).pulled_creation(row.row, {**row.fields, **local.get((row.row_table, row.row), {})}, Actor.system())
        settings = self.tables.rows(Setting.table())
        for setting in self.machine_settings():
            settings.delete(setting, Actor.system())
        for setting in machine_settings:
            settings.save(Setting(environment_id=setting.environment_id, key=setting.key, value=setting.value), Actor.system())

    def machine_settings(self) -> list[Setting]:
        return [setting for setting in self.tables.rows(Setting.table()).rows() if not self.scopes.is_team(setting.key)]

    def local_values(self) -> dict[tuple[str, int], dict]:
        return {(table, row.row_id): values for table in self.tables.names() for row in self.tables.rows(table).rows() if (values := {name: value for name, value in Schema.stored_values(row, None).items() if name in row.local_fields})}

    def laid(self, change: OutgoingChange) -> None:
        rows = self.tables.rows(change.row_table)
        if change.action == DELETED:
            rows.pulled_deletion(change.row, Actor.system())
        elif not rows.pulled_update(change.row, change.fields or {}, Actor.system()):
            rows.pulled_creation(change.row, change.fields or {}, Actor.system())
