import json
from dataclasses import asdict, dataclass, fields
from inspect import getmembers, isfunction
from typing import Callable, ClassVar, get_type_hints

from journal.engine.nudge import Nudge
from journal.engine.support.block import Block
from journal.engine.support.typist import Typist
from journal.events.feature_data import FeatureData
from journal.events.event import Event
from journal.support.permission import Permission
from journal.support.timeout import Timeout
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition

LISTENER = "on_"


@dataclass(frozen=True)
class BaseState:
    """The parent of every state. Its listeners are its on_ methods, bound to the event each hears by its annotation; its answers are unchanged, changed, push, pop, pop_through, which pops and hands the event to the state beneath, and hold, and a listener that stops the event's propagation is the last to hear it. A state coming to the top of the stack or leaving it is handed the typist and may switch it off or on. What every state hears, the compaction and the session's end, is the engine's SafetyConduct, folded in before every feature's."""

    name: ClassVar[str]
    title: ClassVar[str] = ""
    final: ClassVar[bool] = False
    assigner: ClassVar[type | None] = None
    conduct_free: ClassVar[bool] = False
    essential: ClassVar[bool] = False
    allows: ClassVar[frozenset[Permission]] = frozenset()

    def respond(self, event: Event, settings: Settings, conducts: tuple[type[BaseState], ...] = ()) -> Transition:
        return self.answered(event, settings, self.event_listeners(type(event), conducts))

    def answered(self, event: Event, settings: Settings, listeners: tuple[Callable, ...]) -> Transition:
        answers: list[Transition] = []
        event.propagation.reset()
        for listener in listeners:
            answers.append(listener(self, event, settings))
            if not event.propagation.ongoing:
                break
        return Transition.merged(self, answers)

    @classmethod
    def listeners(cls, conducts: tuple[type[BaseState], ...] = ()) -> tuple[tuple[type, Callable], ...]:
        owned = [(get_type_hints(method)["event"], method, method.__name__ not in cls.__dict__) for name, method in getmembers(cls, isfunction) if cls.is_listener(name, method)]
        active_conducts = [conduct for conduct in conducts if not cls.conduct_free or conduct.essential]
        folded = [(get_type_hints(method)["event"], method, 2) for conduct in active_conducts for name, method in getmembers(conduct, isfunction) if cls.is_listener(name, method) and getattr(BaseState, name, None) is not method]
        ranked = sorted([*owned, *folded], key=lambda entry: (int(entry[2]), -len(entry[0].__mro__)))
        return tuple((event_kind, method) for event_kind, method, rank in ranked)

    @classmethod
    def is_listener(cls, name: str, method: Callable) -> bool:
        return name.startswith(LISTENER) and "event" in get_type_hints(method)

    @classmethod
    def event_listeners(cls, event: type, conducts: tuple[type[BaseState], ...] = ()) -> tuple[Callable, ...]:
        return tuple(method for event_kind, method in cls.listeners(conducts) if issubclass(event, event_kind))

    def none(self, *nudges: Nudge) -> Transition:
        return Transition(self, nudges=nudges)

    def swap(self, next: "BaseState", *nudges: Nudge) -> Transition:
        return Transition(next, nudges=nudges)

    def push(self, destination: "BaseState", *nudges: Nudge) -> Transition:
        return Transition(self, pushed=destination, nudges=nudges)

    def pop(self, *nudges: Nudge) -> Transition:
        return Transition(self, popped=True, nudges=nudges)

    def forward(self, *nudges: Nudge) -> Transition:
        return Transition(self, popped=True, nudges=nudges, handed_down=True)

    def refuse(self, reason: Nudge) -> Transition:
        return Transition(self, refusal=reason)

    def on_push(self, settings: Settings) -> tuple[Nudge, ...] | Block:
        return ()

    def on_pause(self, settings: Settings) -> tuple[Nudge, ...]:
        return ()

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...] | Transition:
        return ()

    def on_pop(self, settings: Settings) -> tuple[Nudge, ...]:
        return ()

    def is_waiting(self) -> bool:
        return False

    def blocks_tools(self) -> bool:
        return False

    def mode_lines(self) -> tuple[Nudge, ...]:
        return ()

    def on_enter(self, typist: Typist) -> None:
        return None

    def on_exit(self, typist: Typist) -> None:
        return None

    def serialized(self) -> dict:
        return json.loads(json.dumps(asdict(self)))

    def state_text(self) -> str:
        set_fields = [f"{field.name}={getattr(self, field.name)}" for field in fields(self) if getattr(self, field.name) != field.default and not isinstance(getattr(self, field.name), (float, Timeout))]
        return f"{self.name}({', '.join(set_fields)})" if set_fields else self.name

    @classmethod
    def restored(cls, data: dict) -> "BaseState":
        kinds = {field.name: field.type for field in fields(cls)}
        return cls(**{name: Timeout.parsed(value) if kinds[name] is Timeout else value for name, value in data.items() if name in kinds})
