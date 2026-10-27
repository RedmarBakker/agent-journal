from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class QuestionClosed(RowEvent):
    """The user closed a question that was no longer needed, without an answer."""

    feature_name = "questions"

    question_id: int
