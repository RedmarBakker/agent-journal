import re


class Tags:
    """A command tag from before tags were dropped, [!name], [!name:N], [!name:N,M] or [!name="text"] opening a line of a turn, optionally after > or **: stripped from the chat text and run by nothing."""

    TAG_PATTERN = re.compile(r'^[ \t]*(?:>\s?)?(?:\*\*)?\[!([a-z]+)(?::([0-9]+(?:,[0-9]+)*)|="([^"]*)")?\](?:\*\*)?[ \t]*', re.MULTILINE)

    @classmethod
    def visible(cls, text: str) -> str:
        return cls.TAG_PATTERN.sub("", text).strip()
