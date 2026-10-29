import re


class KeywordMatch:
    """Whether a text names any of a skill's declared words, each a whole word or a phrase of words, in any case."""

    @staticmethod
    def matches(text: str, keywords: tuple[str, ...]) -> bool:
        return any(re.search(KeywordMatch.pattern(keyword), text, re.IGNORECASE) for keyword in keywords if keyword.split())

    @staticmethod
    def pattern(keyword: str) -> str:
        return rf"\b{r'\s+'.join(re.escape(part) for part in keyword.split())}\b"
