from journal.features.workers.workers_options import WorkersOptions


class BaseState:
    """The parent of every state."""


class Wait(BaseState):
    """A pause over the work."""


class Activity:
    """How an agent shows on the agent bar."""

    def question(self, agent) -> int:
        # @sin SessionPurityStateNameComparedDetector
        return agent.data.get("question_id", 0) if agent.state == "waiting" else 0

    def lines(self, settings) -> list:
        # @sin SessionPurityStateNameComparedDetector
        if settings.value(WorkersOptions.MODE) != "orchestrator":
            return []
        return ["hand the next task out"]

    def modes(self, mode: str) -> bool:
        # @sin SessionPurityStateNameComparedDetector
        return mode in ("builder", "solo")

    def command(self, words: list) -> bool:
        # @righteous SessionPurityStateNameComparedDetector
        return words == ["journal", "stuck"]

    def resting(self, state) -> bool:
        # @sin SessionPurityStateTypeCheckedDetector
        return isinstance(state, Wait)

    def asked(self, state) -> int:
        # @righteous SessionPurityStateTypeCheckedDetector
        return state.question_id()
