from pathlib import Path

from journal.features.library.support.portable_body import PortableBody


class ReaderBody:
    """A reader as the library carries it: its file's name, a pattern or a shell script, and the file's text; and back into the file."""

    @staticmethod
    def text(path: Path) -> str:
        return PortableBody.text({"file": path.name, "text": path.read_text()})

    @staticmethod
    def file_name(body: str) -> str:
        return Path(str(PortableBody.fields(body)["file"])).name

    @staticmethod
    def file_text(body: str) -> str:
        return str(PortableBody.fields(body)["text"])
