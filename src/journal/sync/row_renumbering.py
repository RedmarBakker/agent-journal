from journal.config import Config
from journal.db.schema import Schema
from journal.db.table_renumbering import TableRenumbering
from journal.models.all_models import AllModels
from journal.models.environment import Environment
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

    def __init__(self, tables: TableRenumbering, blocks: IdBlocks, supply: BlockSupply, config: Config) -> None:
        self.tables, self.blocks, self.supply, self.config = tables, blocks, supply, config

    def renumbered(self, account_id: int) -> dict[str, dict[int, int]]:
        moves = {model.storage(): self.numbers(model.number_pool(), self.tables.ids(model.storage())) for model in self.stored_models()}
        refs = self.references(moves, {User.table(): {LOCAL_USER: account_id}})
        self.tables.renumbered(moves, self.remaps(refs), refs, self.restamps(Actor.user(LOCAL_USER).stamp, Actor.user(account_id).stamp), (User.storage(),))
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
        refs = self.references(moves, {})
        self.tables.renumbered(moves, self.remaps(refs), refs, [], ())
        self.files_kept(refs)
        return refs

    @staticmethod
    def references(moves: dict[str, dict[int, int]], extra: dict[str, dict[int, int]]) -> dict[str, dict[int, int]]:
        return {**{model.table(): moves[model.storage()] for model in AllModels.MODELS if model.storage() in moves}, **extra}

    @staticmethod
    def remaps(refs: dict[str, dict[int, int]]) -> list[tuple[str, str, dict[int, int]]]:
        environments = refs.get(Environment.table(), {})
        scoped = [(storage, "environment_id", environments) for storage in {model.storage() for model in AllModels.SCOPED}]
        return [*scoped, *((model.storage(), column, refs.get(table, {})) for model, column, table in ROW_REFERENCES)]

    @classmethod
    def restamps(cls, local: str, person: str) -> list[tuple[str, str, str, str]]:
        return [(model.storage(), column.name, local, person) for model in cls.stored_models() for column in Schema.columns(model) if column.column_type is Actor]

    def files_kept(self, refs: dict[str, dict[int, int]]) -> None:
        for table, folder in FOLDERS.items():
            self.files_moved(self.config.files / folder, refs.get(table, {}))

    @staticmethod
    def stored_models() -> list:
        shared = {}
        for model in AllModels.MODELS:
            if model.shared and model.storage() != User.storage():
                shared.setdefault(model.storage(), model)
        return list(shared.values())

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
    def files_moved(folder, numbers: dict[int, int]) -> None:
        held = [(folder / str(old), folder / str(new)) for old, new in numbers.items() if (folder / str(old)).is_dir()]
        for old, new in held:
            old.rename(old.with_name(f"moving-{new.name}"))
        for old, new in held:
            old.with_name(f"moving-{new.name}").rename(new)
