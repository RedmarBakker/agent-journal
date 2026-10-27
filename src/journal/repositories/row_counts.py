from dataclasses import fields
from enum import Enum
from typing import get_type_hints

from journal.db.connection import Connection
from journal.db.query import Query
from journal.models.all_models import AllModels
from journal.models.model import Model
from journal.models.scoped import Scoped
from journal.repositories.scope import Scope
from journal.support.rejection import Rejection


class RowCounts:
    """How many rows of a table have the values named for their fields, in the environment in scope when the table is scoped: what a memory row's condition counts."""

    def __init__(self, connection: Connection, scope: Scope) -> None:
        self.connection, self.scope = connection, scope

    def counted(self, table: str, values: tuple[tuple[str, tuple], ...]) -> int:
        model = self.model(table)
        query = Query.build(model)
        for name, allowed in values:
            query = query.filter_listed(name, allowed)
        if issubclass(model, Scoped):
            query = query.filter(environment_id=self.scope.id)
        return self.connection.result(*query.count())["value"]

    @staticmethod
    def model(table: str) -> type[Model]:
        matches = [candidate for candidate in AllModels.MODELS if candidate.table() == table]
        if not matches:
            raise Rejection(f"no table is named {table!r}")
        return matches[0]

    @classmethod
    def checked(cls, table: str, values: tuple[tuple[str, tuple], ...]) -> None:
        model = cls.model(table)
        names = {column.name for column in fields(model)}
        unknown = [name for name, _ in values if name not in names]
        if unknown:
            raise Rejection(f"{table} has no field {', '.join(unknown)}; its fields are {', '.join(sorted(names))}")
        for name, allowed in values:
            cls.checked_choices(model, name, allowed)

    @staticmethod
    def checked_choices(model: type[Model], name: str, allowed: tuple) -> None:
        type_name = get_type_hints(model)[name]
        if not (isinstance(type_name, type) and issubclass(type_name, Enum)):
            return
        choices = [member.value for member in type_name]
        unknown = [str(value) for value in allowed if value not in choices]
        if unknown:
            raise Rejection(f"{model.table()} {name} is never {', '.join(unknown)}; it is one of {', '.join(choices)}")
