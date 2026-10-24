from typing import ClassVar

from journal.features.messages.support.messages_data import MessagesData
from journal.events.data_source import DataSource


class MessagesPart(DataSource[MessagesData]):
    """The messages feature's part of the feature data."""

    name: ClassVar[str] = "messages"
