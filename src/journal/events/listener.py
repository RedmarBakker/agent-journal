from typing import Generic, TypeVar, get_args

from journal.events.event import Event

E = TypeVar("E", bound=Event)


class Listener(Generic[E]):
    """Receives one kind of event, named in its class as Listener[TheEvent]. Returns what it has to say, or nothing. A helper's hook reaches it only when the helper's file allows the class it is registered as."""

    def handle(self, event: E) -> object:
        return None

    def registered_class(self) -> type:
        return type(self)

    @classmethod
    def event_type(cls) -> type[Event]:
        for klass in cls.__mro__:
            for base in getattr(klass, "__orig_bases__", ()):
                args = get_args(base)
                if args and isinstance(args[0], type) and issubclass(args[0], Event):
                    return args[0]
        raise TypeError(f"{cls.__name__} does not say which event it hears; write it as Listener[TheEvent]")
