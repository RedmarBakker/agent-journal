from typing import TypedDict


class TranscriptHeading(TypedDict):
    """One turn of a transcript as its page lists it: where it is, who wrote it, when, the tools it used and what each call did, and its text when it is spoken."""

    line: int
    speaker: str
    turn_type: str
    time: float
    tools: list[str]
    steps: list[dict]
    text: str
    has_text: bool
