from journal.models.author import Author
from journal.models.message import Message


def stored_by_text(messages, text: str, actor) -> None:
    # @sin AgentWordsWithoutKeyDetector
    messages.save(Message(author=Author.AGENT, text=text), actor)


def stored_by_key(messages, text: str, key: str, actor) -> None:
    # @righteous AgentWordsWithoutKeyDetector
    messages.save(Message(author=Author.AGENT, text=text, idempotency=key), actor)
