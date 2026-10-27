from journal.features.workers.workers_options import WorkersOptions


class BaseState:
    """The parent of every state."""


class Wait(BaseState):
    """A pause over the work."""


class Activity:
    """How an agent shows on the agent bar."""

    def question(self, agent) -> int:
        # @sin StateNameComparedDetector
        return agent.data.get("question_id", 0) if agent.state == "waiting" else 0

    def lines(self, settings) -> list:
        # @sin StateNameComparedDetector
        if settings.value(WorkersOptions.MODE) != "orchestrator":
            return []
        return ["hand the next task out"]

    def modes(self, mode: str) -> bool:
        # @sin StateNameComparedDetector
        return mode in ("builder", "solo")

    def command(self, words: list) -> bool:
        # @righteous StateNameComparedDetector
        return words == ["journal", "stuck"]

    def resting(self, state) -> bool:
        # @sin StateTypeCheckedDetector
        return isinstance(state, Wait)

    def asked(self, state) -> int:
        # @righteous StateTypeCheckedDetector
        return state.question_id()
