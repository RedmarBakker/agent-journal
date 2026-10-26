from dataclasses import dataclass


@dataclass(frozen=True)
class SequencesData:
    """The sequences feature's reading for an agent: the run in hand, its step and whether it is paused or taken up, when the step was last sent, whether a line may be typed to the agent, and what else keeps the step quiet: an open question or a debt to the journal."""

    sequence_id: int
    step: int
    step_text: str
    pause_reason: str
    is_adopted: bool
    step_repeated: bool
    step_silence_seconds: float
    is_typable: bool
    question_open: bool
    obligations_due: bool

    def has_run(self) -> bool:
        return self.sequence_id > 0

    @classmethod
    def empty(cls, step_silence_seconds: float) -> "SequencesData":
        return cls(sequence_id=0, step=0, step_text="", pause_reason="", is_adopted=False, step_repeated=False, step_silence_seconds=step_silence_seconds, is_typable=False, question_open=False, obligations_due=False)
