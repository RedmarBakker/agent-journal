from journal.http.controllers.controller import Controller
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.sequence import Sequence
from journal.models.support.sequence_step import SequenceStep
from journal.models.support.sequence_trigger import SequenceTrigger
from journal.repositories.sequences import Sequences
from journal.support.rejection import Rejection


class SequenceController(Controller[Sequence]):
    """Sequences, read whole with their steps and triggers; one is made here, and the triggers and the steps of one not locked are set here."""

    def __init__(self, sequences: Sequences) -> None:
        self.repository = sequences

    def store(self, request: Request) -> Response:
        title = str(request.body.get("title", "")).strip()
        steps = self.body_steps(request)
        if not title or not steps:
            raise Rejection("a sequence needs a title and at least one step with its instructions")
        sequence = Sequence(title=title, steps=steps, triggers=self.body_triggers(request))
        return Response.json(self.shown(self.repository.save(sequence, request.actor)), 201)

    @staticmethod
    def body_steps(request: Request) -> tuple[SequenceStep, ...]:
        return tuple(step for step in (SequenceStep.parsed(item) for item in request.body.get("steps", [])) if step.instructions.strip())

    @staticmethod
    def body_triggers(request: Request) -> tuple[SequenceTrigger, ...]:
        return tuple(SequenceTrigger.parsed(item).checked() for item in request.body.get("triggers", []))

    def triggers(self, request: Request) -> Response:
        sequence = self.repository.find(request.number("id")).unlocked()
        return Response.json(self.shown(self.repository.save(sequence.with_(triggers=self.body_triggers(request)), request.actor)))

    def steps(self, request: Request) -> Response:
        sequence = self.repository.find(request.number("id")).unlocked()
        return Response.json(self.shown(self.repository.save(sequence.with_(steps=self.body_steps(request)), request.actor)))
