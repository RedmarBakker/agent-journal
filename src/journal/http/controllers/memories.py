from datetime import datetime, timezone

from journal.db.query import Query
from journal.engine.clock import Clock
from journal.http.controllers.controller import Controller
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.memory import Memory
from journal.repositories.memories import Memories

DEFAULT_WEIGHT = 5


class MemoryController(Controller[Memory]):
    """What the agent keeps in mind here, the ones still shown, each with its weight; the user adds, weighs and removes one as the agent does, saved as the user."""

    def __init__(self, memories: Memories, clock: Clock) -> None:
        self.repository, self.clock = memories, clock

    def list_query(self) -> Query:
        return self.repository.shown_query()

    def store(self, request: Request) -> Response:
        memory = Memory(text=str(request.body.get("text", "")), keywords=tuple(request.body.get("keywords", ()))).weighed(int(request.body.get("weight", DEFAULT_WEIGHT)))
        return Response.json(self.shown(self.repository.save(memory, request.actor)), 201)

    def update(self, request: Request) -> Response:
        memory = self.repository.find(request.number("id"))
        memory_text = memory.with_(text=str(request.body["text"])) if "text" in request.body else memory
        memory_weight = memory_text.reweighed(int(request.body["weight"])) if "weight" in request.body else memory_text
        return Response.json(self.shown(self.repository.save(memory_weight, request.actor)))

    def weigh(self, request: Request) -> Response:
        memory = self.repository.find(request.number("id")).reweighed(int(request.body["weight"]))
        return Response.json(self.shown(self.repository.save(memory, request.actor)))

    def remove(self, request: Request) -> Response:
        memory = self.repository.find(request.number("id")).removed(datetime.fromtimestamp(self.clock.time(), timezone.utc))
        return Response.json(self.shown(self.repository.save(memory, request.actor)))
