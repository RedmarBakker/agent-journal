import inspect
from typing import Callable, TypeVar, get_type_hints

T = TypeVar("T")


class Container:
    """Builds an object from the types its __init__ asks for; one instance per type."""

    def __init__(self) -> None:
        self._factories: dict[type, Callable[[], object]] = {}
        self._instances: dict[type, object] = {}

    def bind(self, type_name: type, factory: Callable[[], object]) -> None:
        self._factories[type_name] = factory

    def instance(self, type_name: type[T], value: T) -> None:
        self._instances[type_name] = value

    def get(self, type_name: type[T]) -> T:
        if type_name not in self._instances:
            self._instances[type_name] = self._factories[type_name]() if type_name in self._factories else self.call(type_name)
        instance = self._instances[type_name]
        if not isinstance(instance, type_name):
            raise TypeError(f"the container holds a {type(instance).__name__} for {type_name.__name__}")
        return instance

    def call(self, fn: Callable[..., T]) -> T:
        target = fn.__init__ if inspect.isclass(fn) else fn
        hints = get_type_hints(target)
        kwargs = {}
        for name, parameter in inspect.signature(target).parameters.items():
            if name == "self" or name not in hints:
                continue
            type_name = hints[name]
            if self.is_buildable(type_name, parameter):
                kwargs[name] = self.get(type_name)
        return fn(**kwargs)

    def is_buildable(self, type_name: object, parameter: inspect.Parameter) -> bool:
        return type_name in self._instances or type_name in self._factories or inspect.isclass(type_name) and parameter.default is inspect.Parameter.empty
