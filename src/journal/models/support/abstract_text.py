import re

# the longest a report's or a document's abstract may be, in characters, shared by both and checked by the database too
ABSTRACT_LENGTH_CHARACTERS = 200
# the end of a sentence: a full stop, a question or an exclamation mark before a space or the end
SENTENCE_END = re.compile(r"(?<=[.!?])\s")


class AbstractText:
    """A report's or a document's abstract: one short description, at most ABSTRACT_LENGTH_CHARACTERS long, and, for a row written without one, its body's first sentence cut to that length. A fitted abstract is the one a row arrives with when it is fit, else its body's first sentence, for rows written before abstracts were required."""

    @staticmethod
    def refusal(text: str) -> str:
        if not text.strip():
            return "an abstract is required: one short description of what it says"
        if len(text) > ABSTRACT_LENGTH_CHARACTERS:
            return f"the abstract is {len(text)} characters, longer than {ABSTRACT_LENGTH_CHARACTERS}: say it in one short description"
        return ""

    @classmethod
    def fitted(cls, abstract: str, body: str, title: str) -> str:
        return cls.body_abstract(body, title) if cls.refusal(abstract) else abstract

    @staticmethod
    def body_abstract(body: str, title: str) -> str:
        first_text = next((text.strip().lstrip("-*> ").strip() for text in body.splitlines() if text.strip() and not text.lstrip().startswith(("#", "|", "```"))), "")
        first_sentence = SENTENCE_END.split(first_text, 1)[0] if first_text else title
        return (first_sentence or title or "No description")[:ABSTRACT_LENGTH_CHARACTERS]
