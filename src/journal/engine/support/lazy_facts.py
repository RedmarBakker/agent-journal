from contextlib import AbstractContextManager
from typing import Callable


class LazyFacts:
    """A feature's facts for an agent, each read the first time a listener asks for it, inside the agent's environment, and kept for the rest of the event, so a listener that asks one fact never pays for the others."""

    def __init__(self, fact_readers: dict[str, Callable[[], object]], environment: Callable[[], AbstractContextManager]) -> None:
        self._fact_readers, self._environment = fact_readers, environment
        self._facts: dict[str, object] = {}

    def __getattr__(self, name: str) -> object:
        fact_readers = self.__dict__.get("_fact_readers", {})
        if name not in fact_readers:
            raise AttributeError(name)
        facts = self.__dict__["_facts"]
        if name not in facts:
            with self.__dict__["_environment"]():
                facts[name] = fact_readers[name]()
        return facts[name]
