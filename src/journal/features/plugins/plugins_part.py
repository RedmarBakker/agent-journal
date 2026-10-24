from typing import ClassVar

from journal.features.plugins.support.plugins_data import PluginsData
from journal.events.data_source import DataSource


class PluginsPart(DataSource[PluginsData]):
    """The plugins feature's part of the feature data."""

    name: ClassVar[str] = "plugins"
