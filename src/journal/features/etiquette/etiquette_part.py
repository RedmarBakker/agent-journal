from typing import ClassVar

from journal.features.etiquette.support.etiquette_data import EtiquetteData
from journal.events.data_source import DataSource


class EtiquettePart(DataSource[EtiquetteData]):
    """The etiquette feature's part of the feature data."""

    name: ClassVar[str] = "etiquette"
