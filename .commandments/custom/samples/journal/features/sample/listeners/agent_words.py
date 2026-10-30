from journal.models.author import Author
from journal.models.message import Message


def text_store(messages, text: str, actor) -> None:
    # @sin AgentWordsWithoutKeyDetector
    messages.save(Message(author=Author.AGENT, text=text), actor)


def key_store(messages, text: str, key: str, actor) -> None:
    # @righteous AgentWordsWithoutKeyDetector
    messages.save(Message(author=Author.AGENT, text=text, idempotency=key), actor)
