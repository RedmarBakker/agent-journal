import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from enum import Enum
from types import UnionType
from typing import Union, get_args, get_origin

from journal.support.actor import Actor
from journal.models.support.ref import Ref


@dataclass(frozen=True)
class Column:
    """One model field as the database holds it: its SQL type, and the value both ways. The definition is the column as a table is made with it: its type, and for a text the database bounds, its length checked; the type of a tuple's items, such as SequenceStep in tuple[SequenceStep, ...], lets a stored tuple of records be read back as records."""

    PLAIN = (bool, int, float, str, datetime, Actor, Ref)

    name: str
    kind: type
    characters: tuple[int, ...] = ()
    item_type: type = object

    @classmethod
    def build(cls, name: str, annotation, characters: tuple[int, ...] = ()) -> "Column":
        return cls(name, cls._plain_type(annotation), characters, cls._item_type(annotation))

    @property
    def definition(self) -> str:
        if not self.characters:
            return self.sql_type
        minimum_length, maximum_length = self.characters
        return f"{self.sql_type} NOT NULL CHECK (length({self.name}) BETWEEN {minimum_length} AND {maximum_length})"

    @property
    def sql_type(self) -> str:
        if self.kind is bool or self.kind is int:
            return "INTEGER"
        if self.kind is float:
            return "REAL"
        return "TEXT"

    @property
    def is_enum(self) -> bool:
        return isinstance(self.kind, type) and issubclass(self.kind, Enum)

    @property
    def is_json(self) -> bool:
        return self.kind not in self.PLAIN and not self.is_enum

    def sql(self, value):
        if value is None:
            return None
        if self.is_json:
            return json.dumps(self.json_value(value), default=asdict)
        if isinstance(value, Actor):
            return value.stamp
        if isinstance(value, Ref):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float, str)):
            return value
        return json.dumps(value)

    def parsed(self, value):
        if value is None:
            return None
        if self.kind is Actor:
            return Actor.parse(value)
        if self.kind is Ref:
            return Ref.parse(value)
        if self.kind is datetime:
            return datetime.fromisoformat(value)
        if self.is_enum:
            return self.kind(value)
        if self.kind is bool:
            return bool(value)
        if self.kind in (int, float, str):
            return value
        loaded = json.loads(value)
        if is_dataclass(self.kind):
            return self.kind.parsed(loaded)
        if self.kind is tuple and is_dataclass(self.item_type):
            return tuple(self.item_type.parsed(item) for item in loaded)
        return tuple(loaded) if self.kind is tuple else loaded

    @staticmethod
    def _plain_type(annotation) -> type:
        origin = get_origin(annotation)
        if origin in (Union, UnionType):
            return Column._plain_type(next(arg for arg in get_args(annotation) if arg is not type(None)))
        if origin is not None:
            return origin
        return annotation if isinstance(annotation, type) else object

    @staticmethod
    def _item_type(annotation) -> type:
        arguments = get_args(annotation)
        return arguments[0] if get_origin(annotation) is tuple and arguments and isinstance(arguments[0], type) else object

    @staticmethod
    def json_value(value: object) -> object:
        if hasattr(value, "published"):
            return value.published()
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)
        return value
