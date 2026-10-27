from dataclasses import dataclass
from urllib.parse import unquote

from sync_server.refusal import Refusal

ITEMS_PATH = "/items"
LIBRARY_PATH = "/library"
FILES_SEGMENT = "files"
WITHDRAW_SEGMENT = "withdraw"


@dataclass(frozen=True)
class LibraryPath:
    """A path of the library's routes read into its parts: /items, /items/<type>/<name>, /items/<type>/<name>/withdraw, /items/<type>/<name>/<number> and /items/<type>/<name>/<number>/files/<file path>; a part not given is empty or 0."""

    item_type: str
    name: str
    number: int
    file_name: str
    is_withdrawal: bool

    @classmethod
    def parsed(cls, path: str) -> "LibraryPath":
        parts = [unquote(part) for part in path.removeprefix(ITEMS_PATH).strip("/").split("/") if part]
        if len(parts) == 3 and parts[2] == WITHDRAW_SEGMENT:
            return cls(parts[0], parts[1], 0, "", True)
        if len(parts) in (0, 2):
            return cls(*(parts or ["", ""]), 0, "", False)
        if len(parts) >= 3 and parts[2].isdigit() and (len(parts) == 3 or (len(parts) > 4 and parts[3] == FILES_SEGMENT)):
            return cls(parts[0], parts[1], int(parts[2]), "/".join(parts[4:]), False)
        raise Refusal(f"no such library path: {path}")

    @staticmethod
    def is_library(path: str) -> bool:
        return path == LIBRARY_PATH or path == ITEMS_PATH or path.startswith(f"{ITEMS_PATH}/")
