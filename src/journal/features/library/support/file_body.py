import hashlib
from pathlib import Path

from journal.features.library.support.portable_body import PortableBody

DOCUMENT_SUFFIX = ".md"


class FileBody:
    """A document or a plain file as the library carries it: its file's name and that file's hash under files, the server keeping the bytes apart, so any file, binary too, comes back byte for byte."""

    @staticmethod
    def text(file_name: str, data: bytes) -> str:
        return PortableBody.text({"name": file_name, "files": {file_name: hashlib.sha256(data).hexdigest()}})

    @staticmethod
    def file_name(body: str) -> str:
        return Path(str(PortableBody.fields(body)["name"])).name
