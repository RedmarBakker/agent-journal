from collections.abc import Iterator, Mapping

from journal.engine.support.data_reader import DataReader
from journal.engine.support.helper_part_violation import HelperPartViolation
from journal.models.agent import Agent
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes


class FeatureParts(Mapping[str, object]):
    """The feature data parts of one agent, each read by its feature's reader in the agent's environment the first time a listener asks for it, the time it took stored as a stage; a part refused to a helper raises, naming the feature its file is missing."""

    def __init__(self, readers: dict[str, DataReader], agent: Agent, scope: Scope, stages: StageTimes, refused: frozenset[str]) -> None:
        self.readers, self.agent, self.scope, self.stages, self.refused = readers, agent, scope, stages, refused
        self.read_parts: dict[str, object] = {}

    def __getitem__(self, name: str) -> object:
        if name in self.refused:
            raise HelperPartViolation(f"a {self.agent.role.value} read the {name} part, but its helper file does not turn on that feature")
        if name not in self.read_parts:
            with self.scope.environment(self.agent.environment_id), self.stages.timed(f"facts {name}"):
                self.read_parts[name] = self.readers[name].read(self.agent)
        return self.read_parts[name]

    def __contains__(self, name: object) -> bool:
        return name in self.readers

    def __iter__(self) -> Iterator[str]:
        return iter(self.readers)

    def __len__(self) -> int:
        return len(self.readers)
