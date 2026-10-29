from typing import Self

from journal.models.support.abstract_text import AbstractText


class Abstracted:
    """A model with a title, a body and an abstract written for them: the refusal a bad abstract earns, and the abstract fitted to the body when the row is pulled from the team."""

    def title_words(self) -> str:
        return self.title

    def refusal(self) -> str:
        return AbstractText.refusal(self.abstract)

    def pulled_row(self) -> Self:
        return self.with_(abstract=AbstractText.fitted(self.abstract, self.body, self.title))

    @classmethod
    def pulled_fields(cls, fields: dict) -> dict:
        return {name: value for name, value in fields.items() if name != "abstract" or not AbstractText.refusal(value)}
