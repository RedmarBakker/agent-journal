from dataclasses import dataclass


@dataclass(frozen=True)
class PublishRequest:
    """The body of POST /items/<type>/<name>: what the item is for, its body as JSON naming its files and their hashes, and the publisher's note."""

    description: str
    body: str
    note: str
