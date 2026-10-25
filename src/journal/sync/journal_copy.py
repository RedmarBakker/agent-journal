from typing import Callable

from journal.db.schema import Schema
from journal.models.model import Model
from journal.models.environment import Environment
from journal.models.outgoing_change import DELETED, OutgoingChange
from journal.models.setting import Setting
from journal.repositories.shared_tables import SharedTables
from journal.sync.setting_scopes import SettingScopes
from journal.sync.team_account import TeamAccount
from journal.sync.team_placement import TeamPlacement
from journal.support.actor import Actor
from sync_server.copied_row import CopiedRow
from sync_server.id_ranges import TEAM_NUMBER_SHIFT


class JournalCopy:
    """This journal's rows TeamPlacement sends to the team, as the team server takes them in a full copy, each row's stored values with every field stamped with the row's update time and the highest number each shared table holds below 2^32, of its rows sent or not, for a team of number 0, so its blocks start above every number this journal has given, and none for a team of its own number, whose blocks start at T * 2^32, above every such number; and a team's full copy taken in place of the rows sent to that team, every row TeamPlacement places in no team kept as it is: whole when a journal first joins, whose numbers mean nothing to the team, laid in beside this journal's own rows when it joins a team with a journal, the team's environment a kept one shares a key with left out and its rows put in the kept one, and a kept setting of the team's scope giving way to the team's own; and at an upgrade of the same team the rows stored on this machine alone untouched, the fields a row keeps on this machine alone, as an environment's name, stored on the rows it still holds, and this machine's waiting writes laid on top, so what it has not sent yet still shows here; either way in one transaction, so nothing reading the journal in the meantime sees it half filled, its rows written straight in without the events of new rows, so a copy of the whole team takes seconds, not the database's write lock for a minute. A setting of one machine or one person is never taken from the copy either way, this machine's own kept as they are."""

    def __init__(self, tables: SharedTables, scopes: SettingScopes, placement: TeamPlacement) -> None:
        self.tables, self.scopes, self.placement = tables, scopes, placement

    def rows(self) -> list[CopiedRow]:
        return self.copied(lambda row: self.placement.is_sent_to(row, self.placement.account))

    def team_rows(self, team_key: str) -> list[CopiedRow]:
        return self.copied(lambda row: self.placement.team_key(row) == team_key)

    def copied(self, is_copied: Callable[[Model], bool]) -> list[CopiedRow]:
        return [CopiedRow(table, row.row_id, Schema.team_values(row, None), {name: row.updated_at.timestamp() for name in Schema.team_values(row, None)}) for table in self.tables.names() for row in self.tables.rows(table).rows() if is_copied(row)]

    def taken_numbers(self, rows: tuple[CopiedRow, ...]) -> list[str]:
        numbers: dict[str, list[int]] = {}
        for row in rows:
            if self.tables.has(row.row_table):
                numbers.setdefault(row.row_table, []).append(row.row)
        return [f"{table}:{row.row_id}" for table, ids in numbers.items() for row in self.tables.rows(table).numbered(ids)]

    def highest(self, team_number: int) -> dict:
        if team_number:
            return {}
        return {table: self.tables.highest_number(table, 1 << TEAM_NUMBER_SHIFT) for table in self.tables.names()}

    def replace(self, rows: tuple[CopiedRow, ...], waiting: list[OutgoingChange], account: TeamAccount) -> None:
        with self.tables.transaction():
            self.rebuilt(rows, self.local_values(), account)
            for change in waiting:
                if self.tables.has(change.row_table):
                    self.laid(change)

    def replace_whole(self, rows: tuple[CopiedRow, ...]) -> None:
        with self.tables.transaction():
            self.rebuilt(rows, {}, self.placement.account)

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

    def rebuilt(self, rows: tuple[CopiedRow, ...], local: dict[tuple[str, int], dict], account: TeamAccount) -> None:
        sent = {table: [row.row_id for row in self.tables.rows(table).rows() if self.placement.is_sent_to(row, account)] for table in self.tables.names()}
        for table, numbers in sent.items():
            self.tables.rows(table).clear_numbers(numbers)
        tables: dict[str, list[tuple[int, dict]]] = {table: [] for table in self.tables.names()}
        for row in rows:
            if row.row_table in tables and self.is_copied(row):
                tables[row.row_table].append((row.row, {**row.fields, **local.get((row.row_table, row.row), {})}))
        for table, table_rows in tables.items():
            self.tables.rows(table).restored(table_rows)

    def is_copied(self, row: CopiedRow) -> bool:
        return row.row_table != Setting.table() or self.scopes.is_team(row.fields.get("key", ""))

    def local_values(self) -> dict[tuple[str, int], dict]:
        return {(table, row.row_id): values for table in self.tables.names() for row in self.tables.rows(table).rows() if (values := {name: value for name, value in Schema.stored_values(row, None).items() if name in row.local_fields})}

    def laid(self, change: OutgoingChange) -> None:
        rows = self.tables.rows(change.row_table)
        if change.action == DELETED:
            rows.pulled_deletion(change.row, Actor.system())
        elif not rows.pulled_update(change.row, change.fields or {}, Actor.system()):
            rows.pulled_creation(change.row, change.fields or {}, Actor.system())
