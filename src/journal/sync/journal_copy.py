from journal.db.schema import Schema
from journal.models.environment import Environment
from journal.models.outgoing_change import DELETED, OutgoingChange
from journal.models.setting import Setting
from journal.repositories.shared_tables import SharedTables
from journal.sync.setting_scopes import SettingScopes
from journal.sync.team_placement import TeamPlacement
from journal.support.actor import Actor
from sync_server.copied_row import CopiedRow


class JournalCopy:
    """This journal's rows TeamPlacement sends to the team, as the team server takes them in a full copy, each row's stored values with every field stamped with the row's update time and the highest number each shared table holds; and the team's full copy taken in place of them: whole when a journal first joins, whose numbers mean nothing to the team, laid in beside this journal's own rows when it joins a team with a journal, the team's environment a kept one shares a key with left out and its rows put in the kept one, and a kept setting of the team's scope giving way to the team's own; and at an upgrade of the same team the rows stored on this machine alone untouched, the fields a row keeps on this machine alone, as an environment's name, stored on the rows it still holds, and this machine's waiting writes laid on top, so what it has not sent yet still shows here; either way in one transaction, so nothing reading the journal in the meantime sees it half filled, its rows written straight in without the events of new rows, so a copy of the whole team takes seconds, not the database's write lock for a minute. A setting of one machine or one person is never in the copy either way: this machine's own are stored through it."""

    def __init__(self, tables: SharedTables, scopes: SettingScopes, placement: TeamPlacement) -> None:
        self.tables, self.scopes, self.placement = tables, scopes, placement

    def rows(self) -> list[CopiedRow]:
        return [CopiedRow(table, row.row_id, Schema.team_values(row, None), {name: row.updated_at.timestamp() for name in Schema.team_values(row, None)}) for table in self.tables.names() for row in self.tables.rows(table).rows() if self.placement.is_sent(row)]

    def highest(self, rows: list[CopiedRow]) -> dict:
        return {table: max((row.row for row in rows if row.row_table == table), default=0) for table in self.tables.names()}

    def replace(self, rows: tuple[CopiedRow, ...], waiting: list[OutgoingChange]) -> None:
        with self.tables.transaction():
            self.rebuilt(rows, self.local_values())
            for change in waiting:
                if self.tables.has(change.row_table):
                    self.laid(change)

    def replace_whole(self, rows: tuple[CopiedRow, ...]) -> None:
        with self.tables.transaction():
            self.rebuilt(rows, {})

    def laid_beside(self, rows: tuple[CopiedRow, ...]) -> None:
        kept = {environment.key: environment.row_id for environment in self.tables.rows(Environment.table()).rows()}
        same = {row.row: kept[row.fields.get("key")] for row in rows if row.row_table == Environment.table() and row.fields.get("key") in kept}
        tables: dict[str, list[tuple[int, dict]]] = {table: [] for table in self.tables.names()}
        for row in rows:
            if row.row_table in tables and not (row.row_table == Environment.table() and row.row in same):
                tables[row.row_table].append((row.row, self.placed(row.fields, same)))
        team_settings = {(fields.get("environment_id"), fields.get("key")) for _, fields in tables[Setting.table()]}
        with self.tables.transaction():
            settings = self.tables.rows(Setting.table())
            for setting in settings.rows():
                if self.scopes.is_team(setting.key) and (setting.environment_id, setting.key) in team_settings:
                    settings.delete(setting, Actor.system())
            for table, table_rows in tables.items():
                self.tables.rows(table).restored(table_rows)

    @staticmethod
    def placed(fields: dict, same: dict[int, int]) -> dict:
        placed = dict(fields)
        if fields.get("environment_id") in same:
            placed["environment_id"] = same[fields["environment_id"]]
        for end in ("source", "target"):
            table, _, number = str(fields.get(end, "")).rpartition(":")
            if table == Environment.table() and number.isdigit() and int(number) in same:
                placed[end] = f"{table}:{same[int(number)]}"
        return placed

    def rebuilt(self, rows: tuple[CopiedRow, ...], local: dict[tuple[str, int], dict]) -> None:
        machine_settings = self.machine_settings()
        for table in self.tables.names():
            self.tables.rows(table).clear()
        tables: dict[str, list[tuple[int, dict]]] = {table: [] for table in self.tables.names()}
        for row in rows:
            if row.row_table in tables:
                tables[row.row_table].append((row.row, {**row.fields, **local.get((row.row_table, row.row), {})}))
        for table, table_rows in tables.items():
            self.tables.rows(table).restored(table_rows)
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
