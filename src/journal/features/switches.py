from journal.events.blocking import Blocking
from journal.events.event import Event
from journal.features.feature import Feature
from journal.events.listener import Listener
from journal.features.registry import Registry
from journal.models.scoped import Scoped
from journal.repositories.scope import Scope
from journal.repositories.scope import PROJECT


class Switches(Listener[Event]):
    """A feature's listener on the bus, which runs only where its feature is on, and in the environment its event happened in, with the reason it runs before the answer when its feature lists it there; so a feature switched off has no listener running, by construction. RecordEdit alone still says for itself, by its blocking property, whether an edit a plugin holds is recorded before the answer, until it is split."""

    def __init__(self, feature: type[Feature], inner: Listener, registry: Registry, scope: Scope, reason: Blocking | None = None) -> None:
        self.feature, self.inner, self.registry, self.scope, self.reason = feature, inner, registry, scope, reason

    @property
    def blocking(self) -> Blocking | None:
        if self.reason is not None:
            return self.reason
        return self.inner.blocking if isinstance(getattr(type(self.inner), "blocking", None), property) else None

    def registered_class(self) -> type:
        return type(self.inner)

    def handle(self, event: Event) -> object:
        with self.scope.environment(self.event_environment(event)):
            if not self.registry.is_enabled(self.feature):
                return None
            return self.inner.handle(event)

    def event_environment(self, event: Event) -> int:
        model = getattr(event, "model", None)
        if isinstance(model, Scoped):
            return model.environment_id
        if hasattr(event, "environment_id"):
            return event.environment_id
        return self.scope.id_default(PROJECT)
