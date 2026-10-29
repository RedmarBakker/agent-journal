from journal.models.support.abstract_text import AbstractText


class Abstracted:
    """A model with a title, a body and an abstract written for them: the refusal a bad abstract earns."""

    def title_words(self) -> str:
        return self.title

    def refusal(self) -> str:
        return AbstractText.refusal(self.abstract)

