from journal.config import Config
from journal.db.connection import Connection
from journal.db.schema import Schema
from journal.models.all_models import AllModels
from journal.models.environment import Environment
from journal.models.link import Link
from journal.models.model import Model
from journal.models.task_log import TaskLog
from journal.models.user import User
from journal.models.worker import Worker
from journal.repositories.id_blocks import IdBlocks
from journal.repositories.number_shortage import NumberShortage
from journal.support.actor import Actor
from journal.support.caller import LOCAL_USER
from journal.sync.attachments import FOLDERS
from journal.sync.block_supply import BlockSupply

ROW_REFERENCES = ((TaskLog, "task_id", "tasks"), (Worker, "edited_task", "tasks"))


class RowRenumbering:
    """A joining journal's own shared rows, or the rows entering the team with a number the team server never handed this machine, moved into the team's row number blocks, so no row of the team's takes their numbers: each row given the next number of its table's blocks, and every environment id, link end, task log's and worker's task, and stamp of this machine's person that named one renamed with it, the person named by their team account, and each row's attached files moved to its new number."""

    def __init__(self, connection: Connection, blocks: IdBlocks, supply: BlockSupply, config: Config) -> None:
        self.connection, self.blocks, self.supply, self.config = connection, blocks, supply, config

    def renumbered(self, account_id: int) -> dict[str, dict[int, int]]:
        moves = {model.storage(): self.numbers(model.number_pool(), self.ids(model)) for model in self.stored_models()}
        with self.connection.transaction() as db:
            refs = self.moved(db, moves, {User.table(): {LOCAL_USER: account_id}})
            self.restamped(db, Actor.user(LOCAL_USER).stamp, Actor.user(account_id).stamp)
            db.execute(f"DELETE FROM {User.storage()}")
        self.files_kept(refs)
        return refs

    def into_team(self, rows: list[Model]) -> dict[str, dict[int, int]]:
        stored: dict[str, tuple[str, list[int]]] = {}
        for row in rows:
            if self.blocks.is_given(row.number_pool(), row.row_id):
                continue
            stored.setdefault(row.storage(), (row.number_pool(), []))[1].append(row.row_id)
        moves = {storage: self.numbers(pool, ids) for storage, (pool, ids) in stored.items()}
        if not moves:
            return {}
        with self.connection.transaction() as db:
            refs = self.moved(db, moves, {})
        self.files_kept(refs)
        return refs

    def moved(self, db, moves: dict[str, dict[int, int]], extra: dict[str, dict[int, int]]) -> dict[str, dict[int, int]]:
        refs = {**{model.table(): moves[model.storage()] for model in AllModels.MODELS if model.storage() in moves}, **extra}
        for storage, numbers in moves.items():
            self.moved_ids(db, storage, numbers)
        environments = refs.get(Environment.table(), {})
        for storage in {model.storage() for model in AllModels.SCOPED}:
            self.remapped(db, storage, "environment_id", environments)
        for model, column, table in ROW_REFERENCES:
            self.remapped(db, model.storage(), column, refs.get(table, {}))
        self.linked(db, refs)
        return refs

    def files_kept(self, refs: dict[str, dict[int, int]]) -> None:
        self.connection.cache.cleared()
        for table, folder in FOLDERS.items():
            self.files_moved(self.config.files / folder, refs.get(table, {}))

    @staticmethod
    def stored_models() -> list:
        shared = {}
        for model in AllModels.MODELS:
            if model.shared and model.storage() != User.storage():
                shared.setdefault(model.storage(), model)
        return list(shared.values())

    def ids(self, model) -> list[int]:
        return [row["id"] for row in self.connection.all(f"SELECT id FROM {model.storage()} ORDER BY id")]

    def numbers(self, pool: str, ids: list[int]) -> dict[int, int]:
        return dict(zip(ids, self.taken(pool, len(ids))))

    def taken(self, pool: str, count: int) -> list[int]:
        numbers = self.blocks.taken(pool, count)
        while len(numbers) < count:
            self.supply.refill()
            more = self.blocks.taken(pool, count - len(numbers))
            if not more:
                raise NumberShortage(f"the team server gave no row numbers for {pool}, which this journal's own rows need to keep their place beside the team's")
            numbers.extend(more)
        return numbers

    @staticmethod
    def moved_ids(db, storage: str, numbers: dict[int, int]) -> None:
        db.execute_many(f"UPDATE {storage} SET id = ? WHERE id = ?", [(-new, old) for old, new in numbers.items()])
        db.execute(f"UPDATE {storage} SET id = -id WHERE id < 0")

    @staticmethod
    def remapped(db, storage: str, column: str, numbers: dict[int, int]) -> None:
        rows = db.all(f"SELECT id, {column} AS value FROM {storage}")
        db.execute_many(f"UPDATE {storage} SET {column} = ? WHERE id = ?", [(numbers[row["value"]], row["id"]) for row in rows if row["value"] in numbers])

    @staticmethod
    def linked(db, refs: dict[str, dict[int, int]]) -> None:
        def moved(ref: str) -> str:
            table, _, number = ref.rpartition(":")
            return f"{table}:{refs[table][int(number)]}" if number.isdigit() and int(number) in refs.get(table, {}) else ref
        rows = db.all(f"SELECT id, source, target FROM {Link.storage()}")
        db.execute_many(f"UPDATE {Link.storage()} SET source = ?, target = ? WHERE id = ?", [(moved(row["source"]), moved(row["target"]), row["id"]) for row in rows])

    @staticmethod
    def restamped(db, local: str, person: str) -> None:
        for model in RowRenumbering.stored_models():
            for column in Schema.columns(model):
                if column.column_type is Actor:
                    db.execute(f"UPDATE {model.storage()} SET {column.name} = ? WHERE {column.name} = ?", (person, local))

    @staticmethod
    def files_moved(folder, numbers: dict[int, int]) -> None:
        held = [(folder / str(old), folder / str(new)) for old, new in numbers.items() if (folder / str(old)).is_dir()]
        for old, new in held:
            old.rename(old.with_name(f"moving-{new.name}"))
        for old, new in held:
            old.with_name(f"moving-{new.name}").rename(new)
