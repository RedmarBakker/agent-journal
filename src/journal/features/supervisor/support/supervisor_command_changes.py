from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Iterator

from journal.events.bus import Bus
from journal.events.blocking import Blocking
from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.events.models.deleted import Deleted
from journal.events.models.model_event import ModelEvent
from journal.events.models.updated import Updated
from journal.models.model import Model
from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from journal.supervisor_authority import SUPERVISOR_ACTOR


class SupervisorCommandChanges(Listener[ModelEvent]):
    TABLES: ClassVar[frozenset[str]] = frozenset({"plans", "phases", "tasks", "checks", "links", "messages"})

    def __init__(self, bus: Bus) -> None:
        self._changes: ContextVar[list[dict[str, Any]] | None] = ContextVar("supervisor_command_changes", default=None)
        bus.add_answer_listener(ModelEvent, self, Blocking.NEXT_DECISION)

    @contextmanager
    def capture(self) -> Iterator[list[dict[str, Any]]]:
        changes: list[dict[str, Any]] = []
        token = self._changes.set(changes)
        try:
            yield changes
        finally:
            self._changes.reset(token)

    def handle(self, event: ModelEvent) -> None:
        changes = self._changes.get()
        if (changes is None or event.actor.actor_type != ActorType.PLUGIN
                or event.actor.id != SUPERVISOR_ACTOR or event.model.table() not in self.TABLES):
            return
        if isinstance(event, Created):
            changes.append(self._change(event, None, self._values(event.model)))
        elif isinstance(event, Updated):
            changes.append(self._change(event, self._changed_values(event.previous, event.changed()),
                                        self._changed_values(event.model, event.changed())))
        elif isinstance(event, Deleted):
            changes.append(self._change(event, self._values(event.model), None))

    @staticmethod
    def _change(event: ModelEvent, before: dict[str, Any] | None,
                after: dict[str, Any] | None) -> dict[str, Any]:
        return {
            "event": type(event).__name__.lower(),
            "ref": {"table": event.model.table(), "id": event.model.row_id},
            "before": before,
            "after": after,
        }

    @classmethod
    def _values(cls, model: Model | None) -> dict[str, Any] | None:
        if model is None:
            return None
        return {
            field.name: cls._value(getattr(model, field.name))
            for field in fields(model) if field.name != "events"
        }

    @classmethod
    def matches(cls, model: Model, expected: dict[str, Any]) -> bool:
        values = cls._values(model)
        return values is not None and all(values.get(name) == value for name, value in expected.items())

    @classmethod
    def _changed_values(cls, model: Model | None, names: tuple[str, ...]) -> dict[str, Any] | None:
        if model is None:
            return None
        return {name: cls._value(getattr(model, name)) for name in names}

    @classmethod
    def _value(cls, value: Any) -> Any:
        if isinstance(value, Actor):
            return {"kind": value.actor_type.value, "id": value.id}
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: cls._value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._value(item) for item in value]
        if is_dataclass(value):
            return {field.name: cls._value(getattr(value, field.name)) for field in fields(value)}
        return value
