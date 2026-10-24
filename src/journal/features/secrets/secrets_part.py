from typing import ClassVar

from journal.features.secrets.support.secrets_data import SecretsData
from journal.events.data_source import DataSource


class SecretsPart(DataSource[SecretsData]):
    """The secrets feature's part of the feature data."""

    name: ClassVar[str] = "secrets"
