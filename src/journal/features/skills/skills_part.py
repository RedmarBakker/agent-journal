from typing import ClassVar

from journal.features.skills.support.skills_data import SkillsData
from journal.events.data_source import DataSource


class SkillsPart(DataSource[SkillsData]):
    """The skills feature's part of the feature data."""

    name: ClassVar[str] = "skills"
