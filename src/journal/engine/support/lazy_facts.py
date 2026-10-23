from contextlib import AbstractContextManager
from typing import Callable

from journal.support.stage_times import StageTimes


class LazyFacts:
    """A feature's facts for an agent, each read the first time a listener asks for it, inside the agent's environment, its time kept as a stage, and kept for the rest of the event, so a listener that asks one fact never pays for the others."""

    def __init__(self, feature: str, fact_readers: dict[str, Callable[[], object]], environment: Callable[[], AbstractContextManager], stages: StageTimes) -> None:
        self._feature, self._fact_readers, self._environment, self._stages = feature, fact_readers, environment, stages
        self._facts: dict[str, object] = {}

    def __getattr__(self, name: str) -> object:
        fact_readers = self.__dict__.get("_fact_readers", {})
        if name not in fact_readers:
            raise AttributeError(name)
        facts = self.__dict__["_facts"]
        if name not in facts:
            with self.__dict__["_environment"](), self.__dict__["_stages"].timed(f"fact {self.__dict__['_feature']} {name}"):
                facts[name] = fact_readers[name]()
        return facts[name]
