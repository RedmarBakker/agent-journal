from journal.models.agent import Agent
from journal.support.sequence_run import SequenceRun

# the name the sequence state is stored under in an agent's stack
FOLLOWING_SEQUENCE = "following_sequence"


class StackedRuns:
    """The sequence runs an agent works through, read from the sequence states on its stack, the bottom one first and the one in hand last."""

    @staticmethod
    def runs(agent: Agent) -> list[SequenceRun]:
        return [SequenceRun.build(layer.get("data", {}).get("run", {})) for layer in agent.stack if layer.get("state") == FOLLOWING_SEQUENCE]

    @classmethod
    def current(cls, agent: Agent) -> SequenceRun | None:
        runs = cls.runs(agent)
        return runs[-1] if runs else None
