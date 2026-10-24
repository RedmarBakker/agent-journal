from pathlib import PurePath


class ImageFiles:
    """Which files are pictures, shown as the picture itself in the edits pane and kept without text."""

    SUFFIXES = frozenset((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif"))

    @classmethod
    def is_image(cls, path: str) -> bool:
        return PurePath(path).suffix.lower() in cls.SUFFIXES
