import hashlib
import json

from journal.features.estimates.estimates_options import EstimatesOptions
from journal.repositories.setting_rows import SettingRows
from journal.support.rejection import Rejection


class TaskSizeScale:
    """The configured relative story point scale and its stable version."""

    def __init__(self, settings: SettingRows) -> None:
        self.settings = settings

    def values(self) -> tuple[int, ...]:
        configured = self.settings.option(EstimatesOptions.SIZE_SCALE)
        if not isinstance(configured, (list, tuple)) or not configured:
            raise Rejection("estimates.size_scale must be an ordered list of positive whole numbers")
        values = tuple(self.point(value) for value in configured)
        if any(value < 1 for value in values) or tuple(sorted(set(values))) != values:
            raise Rejection("estimates.size_scale must be an ordered list of distinct positive whole numbers")
        return values

    def display_values(self) -> str:
        return ", ".join(map(str, self.values()))

    def version(self) -> str:
        return self.version_of(self.values())

    def version_of(self, values: tuple[int, ...]) -> str:
        encoded = json.dumps(values, separators=(",", ":"))
        return hashlib.sha256(encoded.encode()).hexdigest()

    def parse(self, value: object) -> int | None:
        return self.parse_with_version(value)[0]

    def parse_with_version(self, value: object) -> tuple[int | None, str]:
        scale = self.values()
        version = self.version_of(scale)
        if value is None or (isinstance(value, str) and value.strip().lower() == "unknown"):
            return None, version
        size = self.point(value)
        if size < 1:
            raise Rejection("a task size is a positive story point value; zero is not a size")
        if size > scale[-1]:
            raise Rejection(f"{size} is above the maximum size {scale[-1]}: split the work into smaller tasks")
        if size not in scale:
            raise Rejection(f"a task size is one of {', '.join(map(str, scale))}, or unknown")
        return size, version

    @staticmethod
    def point(value: object) -> int:
        if type(value) is int:
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        raise Rejection(f"{value!r} is not a whole story point value")
