import queue
import threading
import types
from collections.abc import Iterable
from enum import Enum

from journal.container import Container
from journal.db.connection import Connection
from journal.engine.job_runner import JobRunner
from journal.http.server import Server
from journal.http.share_server import ShareServer
from journal.support.listener_queue import ListenerQueue

THREADED = (Container, Connection, Server, ShareServer, ListenerQueue, JobRunner, threading.local, threading.Thread, threading.Event, queue.Queue)
"""What runs the journal rather than remembers for it: its threads, sockets, pool and queues, and what each thread keeps for itself, are left as they are between tests."""

PLAIN = (type, types.FunctionType, types.MethodType, types.ModuleType, Enum)
"""What has a __dict__ but keeps no state of a journal's."""


class ServiceMemory:
    """What a journal's services remember, taken once and put back on demand: every service's fields, and those of every object it holds, in a field or inside a dict, list, set or tuple, with each container copied down to the objects it holds, so nothing a test changes inside them reaches the next."""

    def __init__(self, services: Iterable[object]) -> None:
        self.fields: dict[int, tuple[object, dict[str, object]]] = {}
        for service in services:
            self.remember(service)

    def put_back(self) -> None:
        for instance, fields in self.fields.values():
            self.restored(instance, fields)

    def remember(self, instance: object) -> None:
        if id(instance) in self.fields or not self.remembers(instance):
            return
        self.fields[id(instance)] = (instance, self.remembered(instance))
        for value in vars(instance).values():
            self.remember_held(value)

    def remember_held(self, value: object) -> None:
        if isinstance(value, dict):
            value = value.values()
        if not isinstance(value, (list, set, tuple, frozenset, type({}.values()))):
            self.remember(value)
            return
        for item in list(value):
            self.remember_held(item)

    @staticmethod
    def remembers(instance: object) -> bool:
        return hasattr(instance, "__dict__") and not isinstance(instance, THREADED + PLAIN)

    @classmethod
    def remembered(cls, instance: object) -> dict[str, object]:
        return {name: cls.copied(value) for name, value in vars(instance).items()}

    @classmethod
    def copied(cls, value: object) -> object:
        if isinstance(value, dict):
            copy = value.copy()
            copy.update((key, cls.copied(item)) for key, item in value.items())
            return copy
        if isinstance(value, list):
            copy = value.copy()
            copy[:] = [cls.copied(item) for item in value]
            return copy
        return value.copy() if isinstance(value, set) else value

    @classmethod
    def restored(cls, instance: object, fields: dict[str, object]) -> None:
        for name in set(vars(instance)) - set(fields):
            object.__delattr__(instance, name)
        for name, value in fields.items():
            current = vars(instance).get(name)
            if isinstance(value, (dict, list, set)) and type(current) is type(value):
                current.clear()
                current.update(cls.copied(value)) if not isinstance(value, list) else current.extend(cls.copied(value))
            else:
                object.__setattr__(instance, name, cls.copied(value))
