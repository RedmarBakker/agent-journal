from typing import ClassVar

from journal.features.questions.support.questions_data import QuestionsData
from journal.events.data_source import DataSource


class QuestionsPart(DataSource[QuestionsData]):
    """The questions feature's part of the feature data."""

    name: ClassVar[str] = "questions"
