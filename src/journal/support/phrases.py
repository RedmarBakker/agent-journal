import re

# a sequence starts on its phrase as the request itself, a short message and not a long one that happens to hold the words
REQUEST_EXTRA_TOKENS = 4


class Phrases:
    """Words matched against what the user or the agent wrote, by whole tokens, lowercase: a phrase anywhere in the text, or a phrase that is the request itself, with at most a few words around it."""

    @staticmethod
    def tokens(text: str) -> list[str]:
        return re.findall(r"[\w;/-]+", text.lower())

    @classmethod
    def contains(cls, text: str, phrase: str) -> bool:
        phrase_tokens = cls.tokens(phrase)
        return bool(phrase_tokens) and f" {' '.join(phrase_tokens)} " in f" {' '.join(cls.tokens(text))} "

    @classmethod
    def is_request(cls, text: str, phrase: str) -> bool:
        return cls.contains(text, phrase) and len(cls.tokens(text)) - len(cls.tokens(phrase)) <= REQUEST_EXTRA_TOKENS
